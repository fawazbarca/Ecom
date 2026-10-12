from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase
from django.urls import reverse

from store.models import Product

from .cart import Cart


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Mug", price=Decimal("12.50"), stock=10
        )

    def _cart(self):
        return Cart(SimpleNamespace(session=self.client.session))

    def test_add_and_len(self):
        cart = self._cart()
        cart.add(self.product, quantity=2)
        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_total_price(), Decimal("25.00"))

    def test_update_quantity(self):
        cart = self._cart()
        cart.add(self.product, quantity=1)
        cart.add(self.product, quantity=5, override_quantity=True)
        self.assertEqual(cart.get_item(self.product)["quantity"], 5)

    def test_remove(self):
        cart = self._cart()
        cart.add(self.product, quantity=1)
        cart.remove(self.product)
        self.assertEqual(len(cart), 0)

    def test_add_view_and_cart_page(self):
        response = self.client.post(
            reverse("cart:cart_add", args=[self.product.id]), {"quantity": 2}
        )
        self.assertRedirects(response, reverse("cart:cart_detail"))
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "Mug")

    def test_cannot_add_more_than_stock(self):
        response = self.client.post(
            reverse("cart:cart_add", args=[self.product.id]),
            {"quantity": 99},
            follow=True,
        )
        self.assertContains(response, "in stock")
        self.assertEqual(len(self._cart()), 0)
