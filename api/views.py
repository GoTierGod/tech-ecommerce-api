from django.shortcuts import render, get_object_or_404, get_list_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import generics
from rest_framework import filters
from rest_framework import viewsets
from . import serializers
from . import models


# Create your views here.
@api_view()
def welcome(request):
    return Response("Welcome")


class ProductViewSet(viewsets.ViewSet):
    def get_queryset(self, product_id=None):
        queryset = models.Product.objects.order_by("id")
        if product_id:
            queryset = queryset.filter(id=product_id)
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = serializers.ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def retrieve(self, request, id):
        queryset = self.get_queryset(product_id=id)
        serializer = serializers.ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=200)


class ImageViewSet(viewsets.ViewSet):
    def get_queryset(self, product_id=None):
        queryset = models.ProductImage.objects.order_by("id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    # def list(self, request):
    #     queryset = self.get_queryset()
    #     serializer = serializers.ProductImageSerializer(queryset, many=True)
    #     return Response(serializer.data, status=200)

    def retrieve(self, request, id):
        is_default = request.query_params.get("is_default")

        queryset = self.get_queryset(product_id=id)
        filtered_queryset = queryset.filter(is_default=is_default)
        serializer = serializers.ProductImageSerializer(filtered_queryset, many=True)
        return Response(serializer.data, status=200)


class ReviewViewSet(viewsets.ViewSet):
    def get_queryset(self, product_id=None):
        queryset = models.Review.objects.order_by("id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    # def list(self, request):
    #     queryset = self.get_queryset()
    #     serializer = serializers.ReviewSerializer(queryset, many=True)
    #     return Response(serializer.data, status=200)

    def retrieve(self, request, id):
        queryset = self.get_queryset(product_id=id)
        serializer = serializers.ReviewSerializer(queryset, many=True)
        return Response(serializer.data, status=200)


class OrderViewSet(viewsets.ViewSet):
    def get_queryset(self, product_id=None):
        queryset = models.Order.objects.order_by("id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    # def list(self, request):
    #     queryset = self.get_queryset()
    #     serializer = serializers.OrderSerializer(queryset, many=True)
    #     return Response(serializer.data, status=200)

    def retrieve(self, request, id):
        queryset = self.get_queryset(product_id=id)
        serializer = serializers.OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=200)
