from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductModelTests(TestCase):
    def test_slug_is_generated(self):
        product = Product.objects.create(name="Blue Widget", price=Decimal("9.99"), stock=3)
        self.assertEqual(product.slug, "blue-widget")

    def test_slug_stays_unique(self):
        Product.objects.create(name="Widget", price=Decimal("1.00"))
        second = Product.objects.create(name="Widget", price=Decimal("1.00"))
        self.assertEqual(second.slug, "widget-2")

    def test_in_stock_property(self):
        self.assertTrue(Product(name="x", price=1, stock=1).in_stock)
        self.assertFalse(Product(name="x", price=1, stock=0).in_stock)


class ProductViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Books")
        self.product = Product.objects.create(
            name="Django Book", price=Decimal("29.99"), stock=5, category=self.category
        )

    def test_list_view(self):
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Book")

    def test_list_filters_by_category(self):
        Product.objects.create(name="Keyboard", price=Decimal("50.00"), stock=1)
        response = self.client.get(reverse("store:product_list"), {"category": "books"})
        self.assertContains(response, "Django Book")
        self.assertNotContains(response, "Keyboard")

    def test_list_search(self):
        response = self.client.get(reverse("store:product_list"), {"q": "django"})
        self.assertContains(response, "Django Book")

    def test_detail_view(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Book")
