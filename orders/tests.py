from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from store.models import Product


class CheckoutTests(TestCase):
    def setUp(self):
        cache.clear()
        self.product = Product.objects.create(
            name="Jacket", price=Decimal("50.00"), stock=5
        )
        self.client.post(
            reverse("cart:cart_add", args=[self.product.id]), {"quantity": 2}
        )

    def _payload(self):
        return {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "phone": "",
            "address": "1 Analytical Engine Way",
            "city": "London",
            "postal_code": "N1",
        }

    def test_checkout_creates_paid_order(self):
        response = self.client.post(reverse("orders:checkout"), self._payload())
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertRedirects(
            response, reverse("orders:order_confirmation", args=[order.id])
        )
        self.assertTrue(order.paid)
        self.assertTrue(order.transaction_id.startswith("SIM-"))
        self.assertEqual(order.total, Decimal("100.00"))
        self.assertEqual(OrderItem.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_cart_is_cleared_after_checkout(self):
        self.client.post(reverse("orders:checkout"), self._payload())
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "Your cart is empty")

    def test_checkout_with_empty_cart_redirects(self):
        self.client.post(reverse("cart:cart_remove", args=[self.product.id]))
        response = self.client.get(reverse("orders:checkout"))
        self.assertRedirects(response, reverse("store:product_list"))

    def test_invalid_form_does_not_create_order(self):
        payload = self._payload()
        payload["email"] = "not-an-email"
        response = self.client.post(reverse("orders:checkout"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_shipping_fee_added_to_small_order(self):
        self.client.post(reverse("cart:cart_remove", args=[self.product.id]))
        cheap = Product.objects.create(name="Sticker", price=Decimal("10.00"), stock=10)
        self.client.post(reverse("cart:cart_add", args=[cheap.id]), {"quantity": 1})
        self.client.post(reverse("orders:checkout"), self._payload())
        order = Order.objects.first()
        self.assertEqual(order.subtotal, Decimal("10.00"))
        self.assertEqual(order.shipping_fee, Decimal("5.00"))
        self.assertEqual(order.total, Decimal("15.00"))
