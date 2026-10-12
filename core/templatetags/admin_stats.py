from django.contrib.auth import get_user_model
from django.db.models import Sum

from django import template

from orders.models import Order
from store.models import Product

register = template.Library()


@register.simple_tag
def admin_stats():
    paid = Order.objects.filter(paid=True)
    return {
        "products": Product.objects.count(),
        "orders": Order.objects.count(),
        "paid_orders": paid.count(),
        "revenue": paid.aggregate(total=Sum("total"))["total"] or 0,
        "users": get_user_model().objects.count(),
    }
