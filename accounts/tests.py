from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from store.models import Product

from .models import Profile

User = get_user_model()


class ProfileModelTests(TestCase):
    def test_profile_created_with_user(self):
        user = User.objects.create_user(username="ada", password="pw-123456")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.full_name, "ada")


class RegistrationTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newbie",
                "first_name": "New",
                "last_name": "Bie",
                "email": "new@example.com",
                "password1": "Complex-Pass-123",
                "password2": "Complex-Pass-123",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertTrue(User.objects.filter(username="newbie").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="newbie").id)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username="a", email="dup@example.com", password="x")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "b",
                "email": "dup@example.com",
                "password1": "Complex-Pass-123",
                "password2": "Complex-Pass-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="b").exists())


class ProfileViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="jane", email="jane@example.com", password="pw-123456"
        )
        self.client.force_login(self.user)

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
        )

    def test_profile_update_saves_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "phone": "555-1234",
                "address": "1 Main St",
                "city": "Springfield",
                "postal_code": "12345",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jane")
        self.assertEqual(self.user.profile.city, "Springfield")

    def test_order_history_only_shows_own_orders(self):
        mine = Order.objects.create(user=self.user, first_name="J", last_name="D", email="jane@example.com", address="a", city="c", postal_code="z")
        other = User.objects.create_user(username="other", password="pw-123456")
        Order.objects.create(user=other, first_name="O", last_name="T", email="o@example.com", address="a", city="c", postal_code="z")
        response = self.client.get(reverse("accounts:order_list"))
        self.assertContains(response, f"Order #{mine.id}")
        self.assertNotContains(response, f"Order #{other.orders.first().id}")


class CheckoutUserLinkTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="buyer", email="buyer@example.com", password="pw-123456"
        )
        self.user.profile.city = "Paris"
        self.user.profile.save()
        self.product = Product.objects.create(name="Item", price=Decimal("20.00"), stock=5)

    def test_checkout_attaches_user_and_prefills(self):
        self.client.force_login(self.user)
        self.client.post(reverse("cart:cart_add", args=[self.product.id]), {"quantity": 1})
        form_page = self.client.get(reverse("orders:checkout"))
        self.assertContains(form_page, "Paris")
        self.client.post(
            reverse("orders:checkout"),
            {
                "first_name": "Buy", "last_name": "Er", "email": "buyer@example.com",
                "phone": "", "address": "2 Rue", "city": "Paris", "postal_code": "75001",
            },
        )
        order = Order.objects.get()
        self.assertEqual(order.user, self.user)
