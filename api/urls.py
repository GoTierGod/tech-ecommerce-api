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
    path(
        "search/categories/<str:search>",
        views.SearchProductCategoriesViewSet.as_view({"get": "list"}),
    ),
    path(
        "search/brands/<str:search>",
        views.SearchProductBrandsViewSet.as_view({"get": "list"}),
    ),
]
