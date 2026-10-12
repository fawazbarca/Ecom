from django.contrib import admin

from .models import SiteSettings

admin.site.site_header = "Ecom Admin"
admin.site.site_title = "Ecom Admin"
admin.site.index_title = "Dashboard"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("store_name", "tagline", "currency_symbol", "contact_email")}),
        ("Landing banner", {"fields": ("hero_image", "hero_title", "hero_subtitle", "hero_link")}),
        ("Shipping", {"fields": ("shipping_fee", "free_shipping_threshold")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
