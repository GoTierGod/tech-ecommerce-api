from django.urls import path, re_path, register_converter
from . import views
from .converters import IntListConverter

register_converter(IntListConverter, "intlist")

urlpatterns = [
    path("", views.routes),
    # Products
    path(
        "products/", views.ProductViewSet.as_view({"get": "list"}), name="product-list"
    ),
    path(
        "products/<int:product_id>",
        views.ProductViewSet.as_view({"get": "retrieve"}),
        name="product-retrieve",
    ),
    # Brands
    path("brands/", views.BrandViewSet.as_view({"get": "list"}), name="brand-list"),
    # Categories
    path(
        "categories/",
        views.CategoryViewSet.as_view({"get": "list"}),
        name="category-list",
    ),
    # Search
    path(
        "search/<str:search>",
        views.SearchViewSet.as_view({"get": "list"}),
        name="search-list",
    ),
    # Customer
    path(
        "customer/",
        views.CustomerViewSet.as_view({"get": "retrieve"}),
        name="customer-retrieve",
    ),
    path(
        "customer/create/",
        views.CustomerViewSet.as_view({"post": "create"}),
        name="customer-create",
    ),
    path(
        "customer/update/",
        views.CustomerViewSet.as_view({"patch": "update"}),
        name="customer-update",
    ),
    path(
        "customer/delete/",
        views.CustomerViewSet.as_view({"delete": "delete"}),
        name="customer-delete",
    ),
    path(
        "customer/interactions/",
        views.CustomerViewSet.as_view({"get": "list"}),
        name="customer-list",
    ),
    # Cart
    path("cart/", views.CartItemViewSet.as_view({"get": "list"}), name="cart-list"),
    path(
        "cart/create/<int:product_id>",
        views.CartItemViewSet.as_view({"post": "create"}),
        name="cart-create",
    ),
    path(
        "cart/delete/<int:product_id>",
        views.CartItemViewSet.as_view({"delete": "delete"}),
        name="cart-delete",
    ),
    path(
        "cart/move/<int:product_id>",
        views.CartItemViewSet.as_view({"patch": "update"}),
        name="cart-update",
    ),
    # Favorites
    path(
        "favorites/",
        views.FavItemViewSet.as_view({"get": "list"}),
        name="favorites-list",
    ),
    path(
        "favorites/create/<int:product_id>",
        views.FavItemViewSet.as_view({"post": "create"}),
        name="favorites-create",
    ),
    path(
        "favorites/delete/<intlist:product_ids>",
        views.FavItemViewSet.as_view({"delete": "delete"}),
        name="favorites-delete",
    ),
    path(
        "favorites/move/<int:product_id>",
        views.FavItemViewSet.as_view({"patch": "update"}),
        name="favorites-update",
    ),
    # Purchase
    path(
        "purchase/",
        views.PurchaseViewSet.as_view({"post": "create"}),
        name="purchase-create",
    ),
    path(
        "purchase/<int:order_id>/update/",
        views.PurchaseViewSet.as_view({"patch": "update"}),
        name="purchase-update",
    ),
    path(
        "purchase/<int:order_id>/delete/",
        views.PurchaseViewSet.as_view({"delete": "delete"}),
        name="purchase-delete",
    ),
    # History
    path(
        "purchase/history/",
        views.PurchaseViewSet.as_view({"get": "list"}),
        name="history-list",
    ),
    path(
        "purchase/history/<int:order_item_id>",
        views.PurchaseViewSet.as_view({"get": "retrieve"}),
        name="history-retrieve",
    ),
    # Reviews
    path(
        "reviews/<int:review_id>/like/",
        views.ReviewViewSet.as_view({"patch": "like"}),
        name="reviews-like",
    ),
    path(
        "reviews/<int:review_id>/dislike/",
        views.ReviewViewSet.as_view({"patch": "dislike"}),
        name="reviews-dislike",
    ),
    path(
        "reviews/<int:review_id>/report/",
        views.ReviewViewSet.as_view({"patch": "report"}),
        name="reviews-report",
    ),
    path(
        "reviews/product/<int:product_id>",
        views.ReviewViewSet.as_view({"get": "list"}),
        name="reviews-list",
    ),
    path(
        "reviews/product/<int:product_id>/create/",
        views.ReviewViewSet.as_view({"post": "create"}),
        name="reviews-create",
    ),
    path(
        "reviews/product/<int:product_id>/update/",
        views.ReviewViewSet.as_view({"patch": "update"}),
        name="reviews-update",
    ),
    path(
        "reviews/product/<int:product_id>/delete/",
        views.ReviewViewSet.as_view({"delete": "delete"}),
        name="reviews-delete",
    ),
    # Coupons
    path("coupons/", views.CouponViewSet.as_view({"get": "list"}), name="coupons-list"),
]
