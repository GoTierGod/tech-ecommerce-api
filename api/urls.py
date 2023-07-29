from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.welcome),
    # products
    path("products/", views.ProductViewSet.as_view({"get": "list"})),
    # specific product details
    path("products/<int:id>", views.ProductViewSet.as_view({"get": "retrieve"})),
    path("products/images/<int:id>", views.ImageViewSet.as_view({"get": "list"})),
    path("products/reviews/<int:id>", views.ReviewViewSet.as_view({"get": "list"})),
    path("products/orders/<int:id>", views.OrderViewSet.as_view({"get": "list"})),
    # brands
    path("brands/", views.BrandViewSet.as_view({"get": "list"})),
    # categories
    path("categories/", views.CategoryViewSet.as_view({"get": "list"})),
    # offers
    path("offers/", views.OffersViewSet.as_view({"get": "list"})),
    path("offers/<str:category>", views.OffersViewSet.as_view({"get": "list"})),
    # best sellers
    path("best-sellers/", views.BestSellersViewSet.as_view({"get": "list"})),
    path(
        "best-sellers/<str:category>", views.BestSellersViewSet.as_view({"get": "list"})
    ),
    # search
    path("search/<str:search>", views.SearchProductViewSet.as_view({"get": "list"})),
    # user
    path(
        "customer/",
        views.CustomerViewSet.as_view({"post": "retrieve"}),
    ),
    path("customer/update/", views.UpdateCustomerViewSet.as_view({"post": "update"})),
    path("customer/create/", views.CreateCustomerViewSet.as_view({"post": "create"})),
]
