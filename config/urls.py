from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("cart/", include("cart.urls", namespace="cart")),
    path("wishlist/", include("wishlist.urls", namespace="wishlist")),
    path("checkout/", include("orders.urls", namespace="orders")),
    path("", include("store.urls", namespace="store")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
