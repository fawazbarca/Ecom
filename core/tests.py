from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from store.models import Product

from .models import SiteSettings


class SiteSettingsTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_load_is_singleton(self):
        first = SiteSettings.load()
        second = SiteSettings.load()
        self.assertEqual(first.pk, 1)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_load_creates_defaults(self):
        settings = SiteSettings.load()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(settings.currency_symbol, "$")

    def test_settings_render_on_storefront(self):
        settings = SiteSettings.load()
        settings.store_name = "Acme Store"
        settings.currency_symbol = "€"
        settings.save()
        Product.objects.create(name="Sample", price=Decimal("9.99"), stock=1)
        response = self.client.get(reverse("store:product_list"))
        self.assertContains(response, "Acme Store")
        self.assertContains(response, "€")


class CartShippingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.product = Product.objects.create(
            name="Thing", price=Decimal("10.00"), stock=100
        )

    def _add(self, quantity):
        self.client.post(
            reverse("cart:cart_add", args=[self.product.id]), {"quantity": quantity}
        )

    def test_shipping_fee_applies_below_threshold(self):
        self._add(1)  # subtotal 10 < default 50
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "Shipping")
        self.assertContains(response, "5.00")

    def test_free_shipping_above_threshold(self):
        self._add(6)  # subtotal 60 >= 50
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertContains(response, "Free")


class HeroBannerTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_hero_title_and_link_render_on_home(self):
        site = SiteSettings.load()
        site.hero_title = "Big Summer Sale"
        site.hero_subtitle = "Up to 50% off"
        site.hero_link = "/products/?category=apparel"
        site.save()
        response = self.client.get(reverse("store:home"))
        self.assertContains(response, "Big Summer Sale")
        self.assertContains(response, "Up to 50% off")
        self.assertContains(response, "/products/?category=apparel")

    def test_hero_absent_on_catalog_page(self):
        site = SiteSettings.load()
        site.hero_title = "Big Summer Sale"
        site.save()
        response = self.client.get(reverse("store:product_list"))
        self.assertNotContains(response, "Big Summer Sale")


class AdminCustomizationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = get_user_model().objects.create_superuser(
            username="boss", email="boss@ecom.test", password="pw-123456"
        )
        self.client.force_login(self.admin)

    def test_dashboard_shows_branding_and_stats(self):
        Product.objects.create(name="Widget", price=Decimal("5.00"), stock=1)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ecom-welcome")
        self.assertContains(response, "admin/css/custom.css")

    def test_site_settings_admin_page_loads(self):
        response = self.client.get(reverse("admin:core_sitesettings_changelist"))
        self.assertEqual(response.status_code, 200)
