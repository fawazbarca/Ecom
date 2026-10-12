from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status", "paid", "total", "created_at")
    list_filter = ("status", "paid", "created_at")
    search_fields = ("email", "first_name", "last_name", "transaction_id")
    readonly_fields = ("transaction_id", "total", "created_at")
    inlines = [OrderItemInline]
