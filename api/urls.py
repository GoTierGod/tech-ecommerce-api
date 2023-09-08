from django.urls import path, re_path, register_converter
from . import views
from .converters import IntListConverter

register_converter(IntListConverter, "intlist")

urlpatterns = [
    path("", views.routes),
    # Products
    path("products/", views.ProductViewSet.as_view({"get": "list"})),
    path(
        "products/<int:product_id>", views.ProductViewSet.as_view({"get": "retrieve"})
    ),
    # Brands
    path("brands/", views.BrandViewSet.as_view({"get": "list"})),
    # Categories
    path("categories/", views.CategoryViewSet.as_view({"get": "list"})),
    # Best Sellers
    path("best-sellers/", views.BestSellersViewSet.as_view({"get": "list"})),
    path(
        "best-sellers/<str:category>", views.BestSellersViewSet.as_view({"get": "list"})
    ),
    # Search
    path("search/<str:search>", views.SearchViewSet.as_view({"get": "list"})),
    # Customer
    path(
        "customer/",
        views.CustomerViewSet.as_view({"get": "retrieve"}),
    ),
    path("customer/create/", views.CustomerViewSet.as_view({"post": "create"})),
    path("customer/update/", views.CustomerViewSet.as_view({"patch": "update"})),
    path("customer/delete/", views.CustomerViewSet.as_view({"delete": "delete"})),
    # Cart
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
    # Favorites
    path("favorites/", views.FavItemViewSet.as_view({"get": "list"})),
    path(
        "favorites/create/<int:id>",
        views.FavItemViewSet.as_view({"post": "create"}),
    ),
    path(
        "favorites/delete/<intlist:ids>",
        views.FavItemViewSet.as_view({"delete": "delete"}),
    ),
    path("favorites/move/<int:id>", views.FavItemViewSet.as_view({"patch": "update"})),
    # Purchase
    path("purchase/", views.PurchaseViewSet.as_view({"post": "create"})),
    path(
        "purchase/<int:order_id>/update/",
        views.PurchaseViewSet.as_view({"patch": "update"}),
    ),
    path(
        "purchase/<int:order_id>/delete",
        views.PurchaseViewSet.as_view({"delete": "delete"}),
    ),
    # History
    path("purchase/history/", views.PurchaseViewSet.as_view({"get": "list"})),
    path(
        "purchase/history/<int:order_item_id>",
        views.PurchaseViewSet.as_view({"get": "retrieve"}),
    ),
    # Reviews
    path(
        "reviews/<int:review_id>/like/", views.ReviewViewSet.as_view({"patch": "like"})
    ),
    path(
        "reviews/<int:review_id>/dislike/",
        views.ReviewViewSet.as_view({"patch": "dislike"}),
    ),
    path(
        "reviews/<int:review_id>/report/",
        views.ReviewViewSet.as_view({"patch": "report"}),
    ),
    path(
        "reviews/product/<int:product_id>", views.ReviewViewSet.as_view({"get": "list"})
    ),
    path(
        "reviews/product/<int:product_id>/create/",
        views.ReviewViewSet.as_view({"post": "create"}),
    ),
    path(
        "reviews/product/<int:product_id>/update/",
        views.ReviewViewSet.as_view({"patch": "update"}),
    ),
    path(
        "reviews/product/<int:product_id>/delete/",
        views.ReviewViewSet.as_view({"delete": "delete"}),
    ),
    # Coupons
    path("coupons/", views.CouponViewSet.as_view({"get": "list"})),
]
