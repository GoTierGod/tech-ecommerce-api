from django.shortcuts import render, get_object_or_404, get_list_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.filters import OrderingFilter
from . import serializers
from . import models


# Create your views here.
@api_view()
def welcome(request):
    return Response("Welcome")


@api_view(["GET"])
def product(request, id=None):
    if id:
        item = get_object_or_404(models.Product.objects.order_by("id"), pk=id)
        serialized_item = serializers.ProductSerializer(item)
        return Response(serialized_item.data)

    else:
        items = models.Product.objects.order_by("id")
        serialized_items = serializers.ProductSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)


@api_view(["GET"])
def image(request, id=None):
    if id:
        items = get_list_or_404(
            models.ProductImage.objects.order_by("id"), product_id=id
        )
        serialized_items = serializers.ProductImageSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)

    else:
        items = models.ProductImage.objects.order_by("id")
        serialized_items = serializers.ProductImageSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)


@api_view(["GET"])
def review(request, id=None):
    if id:
        items = get_list_or_404(models.Review.objects.order_by("id"), product_id=id)
        serialized_items = serializers.ReviewSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)

    else:
        items = models.Review.objects.order_by("id")
        serialized_items = serializers.ReviewSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)


@api_view(["GET"])
def order(request, id=None):
    if id:
        items = get_list_or_404(models.Order.objects.order_by("id"), product_id=id)
        serialized_items = serializers.OrderSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)

    else:
        items = models.Order.objects.order_by("id")
        serialized_items = serializers.OrderSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)
