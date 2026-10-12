from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Product

from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(quantity, 1)

    override = request.POST.get("override") == "1"
    if not override:
        existing = cart.get_item(product)
        current = existing["quantity"] if existing else 0
        if current + quantity > product.stock:
            messages.error(request, f"Only {product.stock} of {product.name} in stock.")
            return redirect(product.get_absolute_url())

    cart.add(product=product, quantity=quantity, override_quantity=override)
    messages.success(request, f"{product.name} added to your cart.")
    return redirect("cart:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart.remove(product)
    else:
        quantity = min(quantity, product.stock)
        cart.add(product=product, quantity=quantity, override_quantity=True)
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")
