from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase
from django.urls import reverse

from store.models import Product

from .wishlist import Wishlist


class WishlistTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Lamp", price=Decimal("30.00"), stock=5
        )

    def _wishlist(self):
        return Wishlist(SimpleNamespace(session=self.client.session))

    def test_add_and_len(self):
        wishlist = self._wishlist()
        wishlist.add(self.product)
        self.assertEqual(len(wishlist), 1)
        self.assertIn(self.product, wishlist)

    def test_add_is_idempotent(self):
        wishlist = self._wishlist()
        wishlist.add(self.product)
        wishlist.add(self.product)
        self.assertEqual(len(wishlist), 1)

    def test_remove(self):
        wishlist = self._wishlist()
        wishlist.add(self.product)
        wishlist.remove(self.product)
        self.assertEqual(len(wishlist), 0)

    def test_toggle_returns_state(self):
        wishlist = self._wishlist()
        self.assertTrue(wishlist.toggle(self.product))
        self.assertFalse(wishlist.toggle(self.product))

    def test_toggle_view_and_page(self):
        response = self.client.post(
            reverse("wishlist:wishlist_toggle", args=[self.product.id])
        )
        self.assertRedirects(response, reverse("wishlist:wishlist_detail"))
        response = self.client.get(reverse("wishlist:wishlist_detail"))
        self.assertContains(response, "Lamp")

    def test_redirects_to_next(self):
        response = self.client.post(
            reverse("wishlist:wishlist_toggle", args=[self.product.id]),
            {"next": self.product.get_absolute_url()},
        )
        self.assertRedirects(response, self.product.get_absolute_url())
