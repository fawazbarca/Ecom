from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("about/", views.about, name="about"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]
