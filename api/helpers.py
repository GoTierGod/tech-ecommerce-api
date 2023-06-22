from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from . import serializers
from . import models

from distutils.util import strtobool


def make_card_product(product):
    return {
        "details": serializers.ProductSerializer(product).data,
        "image": serializers.ProductImageSerializer(
            models.ProductImage.objects.get(product_id=product.id, is_default=True)
        ).data,
        "sold": models.Order.objects.filter(product_id=product.id).count(),
    }


def make_detailed_product(product):
    return {
        "details": serializers.ProductSerializer(product).data,
        "images": serializers.ProductImageSerializer(
            models.ProductImage.objects.filter(product_id=product.id).order_by("id"),
            many=True,
        ).data,
        "sold": models.Order.objects.filter(product_id=product.id).count(),
        "reviews_counter": models.Review.objects.filter(product_id=product.id).count(),
        "rating": models.Review.objects.filter(product_id=product.id).aggregate(
            Avg("rating")
        )["rating__avg"],
    }


def product_filters(queryset, request):
    category = request.query_params.get("category")
    brand = request.query_params.get("brand")
    min_price = request.query_params.get("min_price")
    max_price = request.query_params.get("max_price")
    installments = request.query_params.get("installments")
    is_gamer = request.query_params.get("is_gamer")

    if category:
        queryset = queryset.filter(category__title__iexact=category)
    if brand:
        queryset = queryset.filter(brand__name__iexact=brand)
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
    if is_gamer:
        queryset = queryset.filter(is_gamer=strtobool(is_gamer))

    return queryset
