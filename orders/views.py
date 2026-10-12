import uuid

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from cart.cart import Cart
from store.models import Product

from .forms import CheckoutForm
from .models import Order, OrderItem


def simulate_payment(order):
    """Stand-in for a real gateway.

    Returns True on success. Replace the body with a Stripe/Razorpay call later;
    the rest of the checkout flow does not need to change.
    """
    order.paid = True
    order.status = "paid"
    order.transaction_id = f"SIM-{uuid.uuid4().hex[:16].upper()}"
    order.save(update_fields=["paid", "status", "transaction_id"])
    return True


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("store:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order(**form.cleaned_data)
            order.save()

            for item in cart:
                product = item["product"]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=item["price"],
                    quantity=item["quantity"],
                )
                product.stock = max(product.stock - item["quantity"], 0)
                product.save(update_fields=["stock"])

            order.recalculate_total()
            order.save(update_fields=["total"])
            simulate_payment(order)
            cart.clear()
            return redirect("orders:order_confirmation", order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"cart": cart, "form": form})


def order_confirmation(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    return render(request, "orders/confirmation.html", {"order": order})
