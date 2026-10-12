from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from core.models import SiteSettings
from store.models import Category, Product

CATEGORIES = {
    "Electronics": [
        "Wireless Headphones", "Smart Watch", "Bluetooth Speaker", "Mechanical Keyboard",
        "USB-C Hub", "Noise Cancelling Earbuds", "Portable Charger", "Webcam HD",
        "Wireless Mouse", "LED Desk Lamp", "Smartphone Stand", "HDMI Cable",
    ],
    "Home & Kitchen": [
        "Ceramic Mug Set", "Cast Iron Pan", "French Press", "Throw Blanket",
        "Chef Knife", "Cutting Board", "Coffee Grinder", "Glass Storage Jars",
        "Non-Stick Skillet", "Electric Kettle", "Dinner Plate Set", "Bamboo Utensils",
    ],
    "Apparel": [
        "Cotton T-Shirt", "Denim Jacket", "Running Shoes", "Wool Beanie",
        "Leather Belt", "Hooded Sweatshirt", "Chino Pants", "Baseball Cap",
        "Socks 3-Pack", "Rain Jacket", "Flannel Shirt", "Canvas Tote Bag",
    ],
}

COLORS = {
    "Electronics": (79, 70, 229),
    "Home & Kitchen": (16, 185, 129),
    "Apparel": (244, 63, 94),
}


def make_placeholder(name, color):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (600, 600), color)
    draw = ImageDraw.Draw(img)
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    draw.text((300, 300), initials, fill=(255, 255, 255), anchor="mm", font_size=180)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return ContentFile(buffer.getvalue())


def make_hero(title):
    from PIL import Image, ImageDraw

    width, height = 1600, 700
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    top = (79, 70, 229)
    bottom = (139, 92, 246)
    for y in range(height):
        ratio = y / height
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    draw.text(
        (width // 2, height // 2),
        title or "Welcome",
        fill=(255, 255, 255),
        anchor="mm",
        font_size=110,
    )
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=88)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Seed the store with sample categories and products."

    @transaction.atomic
    def handle(self, *args, **options):
        created_products = 0
        for category_name, product_names in CATEGORIES.items():
            category, _ = Category.objects.get_or_create(
                slug=slugify(category_name), defaults={"name": category_name}
            )
            for index, product_name in enumerate(product_names):
                product, created = Product.objects.get_or_create(
                    slug=slugify(product_name),
                    defaults={
                        "name": product_name,
                        "category": category,
                        "description": (
                            f"{product_name} — a great pick from our {category_name} range. "
                            "High quality, fair price, and ready to ship."
                        ),
                        "price": Decimal("19.99") + Decimal(index * 10),
                        "stock": 10 + index * 5,
                        "is_active": True,
                        "is_featured": index < 2,
                    },
                )
                if not created and index < 2 and not product.is_featured:
                    product.is_featured = True
                    product.save(update_fields=["is_featured"])
                if created:
                    product.image.save(
                        f"{product.slug}.jpg",
                        make_placeholder(product_name, COLORS[category_name]),
                        save=True,
                    )
                    created_products += 1

        site = SiteSettings.load()
        if not site.hero_image:
            site.hero_title = site.hero_title or site.store_name
            site.hero_subtitle = site.hero_subtitle or "Discover our latest products, curated just for you."
            site.hero_link = site.hero_link or "/products/?category=electronics"
            site.hero_image.save("hero.jpg", make_hero(site.hero_title), save=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(CATEGORIES)} categories and {created_products} new products."
            )
        )
