from decimal import Decimal

from django.conf import settings

from store.models import Product


class Cart:
    """A session-backed shopping cart."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.cart[product_id]["quantity"] = max(self.cart[product_id]["quantity"], 0)
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        by_id = {str(product.id): product for product in products}
        for product_id, stored in self.cart.items():
            product = by_id.get(product_id)
            if product is None:
                continue
            price = Decimal(stored["price"])
            yield {
                "product": product,
                "quantity": stored["quantity"],
                "price": price,
                "line_total": price * stored["quantity"],
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def get_shipping_fee(self):
        from core.models import SiteSettings

        settings = SiteSettings.load()
        subtotal = self.get_total_price()
        if not len(self):
            return Decimal("0.00")
        threshold = settings.free_shipping_threshold
        if threshold and subtotal >= threshold:
            return Decimal("0.00")
        return settings.shipping_fee

    def get_grand_total(self):
        return self.get_total_price() + self.get_shipping_fee()

    def get_item(self, product):
        return self.cart.get(str(product.id))
