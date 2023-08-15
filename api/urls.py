from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.routes),
    # products
    path("products/", views.ProductViewSet.as_view({"get": "list"})),
    path("products/<int:id>", views.ProductViewSet.as_view({"get": "retrieve"})),
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
        views.CustomerViewSet.as_view({"get": "retrieve"}),
    ),
    path("customer/create/", views.CustomerViewSet.as_view({"post": "create"})),
    path("customer/update/", views.CustomerViewSet.as_view({"patch": "update"})),
    path("customer/delete/", views.CustomerViewSet.as_view({"delete": "delete"})),
    # cart
    path("cart/", views.CardItemViewSet.as_view({"get": "list"})),
    path(
        "cart/create/<int:id>",
        views.CardItemViewSet.as_view({"post": "create"}),
    ),
    path(
        "cart/delete/<int:id>",
        views.CardItemViewSet.as_view({"delete": "delete"}),
    ),
    path("cart/move/<int:id>", views.CardItemViewSet.as_view({"patch": "update"})),
    # favorites
    path("favorites/", views.FavItemViewSet.as_view({"get": "list"})),
    path(
        "favorites/create/<int:id>",
        views.FavItemViewSet.as_view({"post": "create"}),
    ),
    path(
        "favorites/delete/<int:id>",
        views.FavItemViewSet.as_view({"delete": "delete"}),
    ),
    path("favorites/move/<int:id>", views.FavItemViewSet.as_view({"patch": "update"})),
    # purchase
    path("purchase/", views.PurchaseViewSet.as_view({"post": "create"})),
]
