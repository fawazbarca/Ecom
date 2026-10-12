from django.conf import settings

from store.models import Product


class Wishlist:
    """A session-backed wishlist storing product ids."""

    def __init__(self, request):
        self.session = request.session
        wishlist = self.session.get(settings.WISHLIST_SESSION_ID)
        if wishlist is None:
            wishlist = self.session[settings.WISHLIST_SESSION_ID] = []
        self.wishlist = wishlist

    def add(self, product):
        product_id = product.id
        if product_id not in self.wishlist:
            self.wishlist.append(product_id)
            self.save()

    def remove(self, product):
        product_id = product.id
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            self.save()

    def toggle(self, product):
        if product.id in self.wishlist:
            self.remove(product)
            return False
        self.add(product)
        return True

    def clear(self):
        self.session[settings.WISHLIST_SESSION_ID] = []
        self.session.modified = True

    def save(self):
        self.session.modified = True

    def contains(self, product):
        return product.id in self.wishlist

    def __contains__(self, product):
        return product.id in self.wishlist

    def __iter__(self):
        products = Product.objects.filter(id__in=self.wishlist, is_active=True)
        by_id = {p.id: p for p in products}
        for product_id in self.wishlist:
            if product_id in by_id:
                yield by_id[product_id]

    def __len__(self):
        return len(self.wishlist)
