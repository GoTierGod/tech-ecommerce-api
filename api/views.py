from django.shortcuts import render, get_object_or_404, get_list_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from . import serializers
from . import models


# Create your views here.
@api_view()
def welcome(request):
    return Response("Welcome")


@api_view(["GET"])
def product(request, id=None):
    if id:
        item = get_object_or_404(models.Product, pk=id)
        serialized_item = serializers.ProductSerializer(item)
        return Response(serialized_item.data)

    else:
        items = models.Product.objects.all()
        serialized_items = serializers.ProductSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)


@api_view(["GET"])
def images(request, id=None):
    if id:
        items = get_list_or_404(models.ProductImage, product_id=id)
        serialized_items = serializers.ProductImageSerializer(items, many=True)
        return Response(serialized_items.data, status.HTTP_200_OK)
