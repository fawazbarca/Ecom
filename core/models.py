from decimal import Decimal

from django.core.cache import cache
from django.db import models


class SiteSettings(models.Model):
    """Singleton site-wide configuration, editable in the admin."""

    store_name = models.CharField(max_length=120, default="Ecom")
    tagline = models.CharField(
        max_length=200, blank=True, default="Demo store — payments are simulated."
    )
    currency_symbol = models.CharField(max_length=8, default="$")
    contact_email = models.EmailField(blank=True, default="support@ecom.test")
    shipping_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("5.00")
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("50.00"),
        help_text="Orders at or above this subtotal ship free. Use 0 to disable free shipping.",
    )
    hero_image = models.ImageField(
        upload_to="hero/",
        blank=True,
        null=True,
        help_text="Full-width banner shown at the top of the landing page.",
    )
    hero_title = models.CharField(max_length=120, blank=True, default="")
    hero_subtitle = models.CharField(max_length=200, blank=True, default="")
    hero_link = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Optional URL the banner button links to (leave blank to hide the button).",
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("site_settings")

    def delete(self, *args, **kwargs):
        cache.delete("site_settings")
        super().delete(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cache.get("site_settings")
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set("site_settings", obj)
        return obj
