from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome),
    path("product/", views.product),
    path("product/<int:id>", views.product),
    path("product/images/<int:id>", views.images),
]
