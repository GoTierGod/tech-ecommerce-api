from django.db.models import Avg, Count, Sum

from . import serializers
from . import models

from distutils.util import strtobool


def is_best_seller(product):
    products = models.Product.objects.all()

    best_sellers = (
        models.OrderItem.objects.values("product")
        .annotate(order_count=Count("id"), total_quantity=Sum("quantity"))
        .order_by("-order_count")[:25]
    )

    bs_products = [item["product"] for item in best_sellers]

    products = products.filter(id__in=bs_products)
    return products.filter(id=product.id).exists()


def compose_product_info(product):
    return {
        "details": serializers.ProductSerializer(product).data,
        "default_img": serializers.ProductImageSerializer(
            models.ProductImage.objects.get(product_id=product.id, is_default=True)
        ).data,
        "images": serializers.ProductImageSerializer(
            models.ProductImage.objects.filter(product_id=product.id),
            many=True,
        ).data,
        "sold": sum(
            [
                item.quantity
                for item in models.OrderItem.objects.filter(product_id=product.id)
            ]
        ),
        "best_seller": is_best_seller(product),
        "reviews_counter": models.Review.objects.filter(product_id=product.id).count(),
        "rating": models.Review.objects.filter(product_id=product.id).aggregate(
            Avg("rating")
        )["rating__avg"],
    }


def product_filters(products, request):
    category = request.query_params.get("category")
    brand = request.query_params.get("brand")
    is_gamer = request.query_params.get("is_gamer")
    min_price = request.query_params.get("min_price")
    max_price = request.query_params.get("max_price")
    installments = request.query_params.get("installments")

    if category:
        products = products.filter(category__title__iexact=category)
    if brand:
        products = products.filter(brand__name__iexact=brand)
    if is_gamer:
        products = products.filter(is_gamer=strtobool(is_gamer))
    if min_price:
        try:
            products = products.filter(offer_price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(offer_price__lte=float(max_price))
        except ValueError:
            pass
    if installments:
        try:
            products = products.filter(installments=int(installments))
        except ValueError:
            pass

    return products


def compose_purchase(order_item):
    return {
        "order": serializers.OrderSerializer(order_item.order).data,
        "order_item": serializers.OrderItemSerializer(order_item).data,
        "is_reviewed": models.Review.objects.filter(id=order_item.product.id).exists(),
    }
