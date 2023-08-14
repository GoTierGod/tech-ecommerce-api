from django.db.models import Avg, Count

from . import serializers
from . import models

from distutils.util import strtobool


def is_best_seller(product):
    queryset = models.Product.objects.all()

    best_sellers = models.Order.objects.values("product").annotate(
        order_count=Count("id")
    )[:25]

    bs_products = [item["product"] for item in best_sellers]

    queryset = queryset.filter(id__in=bs_products)
    return True if queryset.filter(id=product.id) else False


def compose_product_info(product):
    return {
        "details": serializers.ProductSerializer(product).data,
        "default_img": serializers.ProductImageSerializer(
            models.ProductImage.objects.get(product_id=product.id, is_default=True)
        ).data,
        "images": serializers.ProductImageSerializer(
            models.ProductImage.objects.filter(product_id=product.id).order_by("id"),
            many=True,
        ).data,
        "sold": models.Order.objects.filter(product_id=product.id).count(),
        "best_seller": is_best_seller(product),
        "reviews_counter": models.Review.objects.filter(product_id=product.id).count(),
        "rating": models.Review.objects.filter(product_id=product.id).aggregate(
            Avg("rating")
        )["rating__avg"],
    }


def product_filters(queryset, request):
    category = request.query_params.get("category")
    brand = request.query_params.get("brand")
    is_gamer = request.query_params.get("is_gamer")
    min_price = request.query_params.get("min_price")
    max_price = request.query_params.get("max_price")
    installments = request.query_params.get("installments")

    if category:
        queryset = queryset.filter(category__title__iexact=category)
    if brand:
        queryset = queryset.filter(brand__name__iexact=brand)
    if is_gamer:
        queryset = queryset.filter(is_gamer=strtobool(is_gamer))
    if min_price:
        try:
            queryset = queryset.filter(offer_price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            queryset = queryset.filter(offer_price__lte=float(max_price))
        except ValueError:
            pass
    if installments:
        try:
            queryset = queryset.filter(installments=int(installments))
        except ValueError:
            pass

    return queryset
