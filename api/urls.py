from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome),
    path("products/", views.ProductViewSet.as_view({"get": "list"})),
    path("products/<int:id>", views.ProductViewSet.as_view({"get": "retrieve"})),
    path("products/images/<int:id>", views.ImageViewSet.as_view({"get": "list"})),
    path("products/reviews/<int:id>", views.ReviewViewSet.as_view({"get": "list"})),
    path("products/orders/<int:id>", views.OrderViewSet.as_view({"get": "list"})),
]
