from rest_framework.response import Response
from django.db.models import Avg, Count, Sum
from rest_framework.request import Request
from django.db.models.manager import BaseManager

from . import serializers
from . import models

from distutils.util import strtobool


def compose_customer(customer: models.Customer):
    return {
        "id": customer.pk,
        "username": customer.user.username,
        "email": customer.user.email,
        "first_name": customer.user.first_name,
        "last_name": customer.user.last_name,
        "birthdate": str(customer.birthdate),
        "gender": customer.gender,
        "phone": customer.phone,
        "country": customer.country,
        "city": customer.city,
        "address": customer.address,
        "points": customer.points,
    }


def compose_product(product: models.Product):
    return {
        "details": serializers.ProductSerializer(product).data,
        "default_img": serializers.ProductImageSerializer(
            models.ProductImage.objects.get(product=product, is_default=True)
        ).data,
        "images": serializers.ProductImageSerializer(
            models.ProductImage.objects.filter(product=product),
            many=True,
        ).data,
        "sold": models.OrderItem.objects.filter(product=product).count(),
        "best_seller": is_best_seller(product),
        "reviews_counter": models.Review.objects.filter(product=product).count(),
        "rating": models.Review.objects.filter(product=product).aggregate(
            Avg("rating")
        )["rating__avg"],
    }


def compose_purchase(order_item: models.OrderItem):
    return {
        "order": serializers.OrderSerializer(order_item.order).data,
        "order_item": serializers.OrderItemSerializer(order_item).data,
        "product": compose_product(order_item.product),
        "is_reviewed": models.Review.objects.filter(
            product=order_item.product, customer=order_item.order.customer
        ).exists(),
    }


def compose_review(review: models.Review):
    return {
        "review": serializers.ReviewSerializer(review).data,
        "likes": models.ReviewLike.objects.filter(review=review).count(),
        "dislikes": models.ReviewDislike.objects.filter(review=review).count(),
    }


def filter_products(products: BaseManager[models.Product], request: Request):
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
        products = products.filter(offer_price__gte=min_price)
    if max_price:
        products = products.filter(offer_price__lte=max_price)
    if installments:
        products = products.filter(installments=installments)

    return products


def is_best_seller(product: models.Product):
    products = models.Product.objects.all()

    best_sellers = (
        models.OrderItem.objects.values("product")
        .annotate(order_count=Count("id"), total_quantity=Sum("quantity"))
        .order_by("-order_count")[:25]
    )

    bs_products = [item["product"] for item in best_sellers]

    products = products.filter(id__in=bs_products)
    return products.filter(id=product.id).exists()
