from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def home(request):
    featured = list(Product.objects.filter(is_active=True, is_featured=True)[:6])
    if not featured:
        featured = list(Product.objects.filter(is_active=True)[:6])
    return render(request, "store/home.html", {"featured": featured})


def about(request):
    return render(request, "store/about.html")


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()

    category_slug = request.GET.get("category")
    query = request.GET.get("q", "").strip()

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(products, 36)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "current_category": current_category,
        "query": query,
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    related = Product.objects.filter(
        is_active=True, category=product.category
    ).exclude(pk=product.pk)[:4]
    return render(
        request,
        "store/product_detail.html",
        {"product": product, "related": related},
    )
