from django.db.models import Avg

from . import serializers
from . import models


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
