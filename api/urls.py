from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.welcome),
    path("products/", views.ProductViewSet.as_view({"get": "list"})),
    path("products/<int:id>", views.ProductViewSet.as_view({"get": "retrieve"})),
    path("products/images/<int:id>", views.ImageViewSet.as_view({"get": "list"})),
    path("products/reviews/<int:id>", views.ReviewViewSet.as_view({"get": "list"})),
    path("products/orders/<int:id>", views.OrderViewSet.as_view({"get": "list"})),
    path("brands/", views.BrandViewSet.as_view({"get": "list"})),
    path("categories/", views.CategoryViewSet.as_view({"get": "list"})),
    path("offers/", views.OffersViewSet.as_view({"get": "list"})),
    path("offers/<str:category>", views.OffersViewSet.as_view({"get": "list"})),
    path("best-sellers/", views.BestSellersViewSet.as_view({"get": "list"})),
    path(
        "best-sellers/<str:category>", views.BestSellersViewSet.as_view({"get": "list"})
    ),
    path("search/<str:search>", views.SearchViewSet.as_view({"get": "list"})),
]
