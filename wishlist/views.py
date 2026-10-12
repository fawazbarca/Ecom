from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Product

from .wishlist import Wishlist


def wishlist_detail(request):
    wishlist = Wishlist(request)
    return render(request, "wishlist/detail.html", {"wishlist": wishlist})


@require_POST
def wishlist_toggle(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    added = wishlist.toggle(product)
    if added:
        messages.success(request, f"{product.name} added to your wishlist.")
    else:
        messages.success(request, f"{product.name} removed from your wishlist.")
    return redirect(request.POST.get("next") or "wishlist:wishlist_detail")
