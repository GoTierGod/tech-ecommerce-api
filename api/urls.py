from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome),
    path("product/", views.product),
    path("product/<int:id>", views.product),
    path("product/image/", views.image),
    path("product/image/<int:id>", views.image),
    path("product/review/", views.review),
    path("product/review/<int:id>", views.review),
    path("product/order/", views.order),
    path("product/order/<int:id>", views.order),
]
