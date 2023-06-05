from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.db.models import Avg
from . import serializers
from . import models


# Create your views here.
@api_view()
def welcome(request):
    return Response("Welcome")


class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
        # allowed filters to be passed by query parameters
        category = request.query_params.get("category")
        brand = request.query_params.get("brand")

        # product queryset
        queryset = models.Product.objects.order_by("id")

        # filter if the allowed query parameters are present
        if category:
            queryset = queryset.filter(
                category_id=get_object_or_404(
                    models.Category, title__iexact=category
                ).id
            )
        if brand:
            queryset = queryset.filter(
                brand_id=get_object_or_404(models.Brand, name__iexact=brand).id
            )

        # return a response containing the required products
        products = []
        for product in queryset:
            products.append(
                {
                    "details": serializers.ProductSerializer(product).data,
                    "image": serializers.ProductImageSerializer(
                        models.ProductImage.objects.filter(product_id=product.id).get(
                            is_default=True
                        )
                    ).data,
                    "sold": models.Order.objects.filter(product_id=product.id).count(),
                }
            )

        return Response(products, status=200)

    def retrieve(self, request, id):
        # product
        product = models.Product.objects.get(id=id)
        serialized_product = serializers.ProductSerializer(product)

        # product images
        images = models.ProductImage.objects.filter(product_id=id)
        serialized_images = serializers.ProductImageSerializer(images, many=True)

        # number of times this product has been sold
        sold = models.Order.objects.filter(product_id=id).count()

        # number of reviews this product has received
        reviews_counter = models.Review.objects.filter(product_id=id).count()

        # product rating
        rating = models.Review.objects.filter(product_id=id).aggregate(Avg("rating"))[
            "rating__avg"
        ]

        # return a response contained the above data
        return Response(
            {
                "details": serialized_product.data,
                "images": serialized_images.data,
                "sold": sold,
                "reviews_counter": reviews_counter,
                "rating": rating,
            },
            status=200,
        )


class ImageViewSet(viewsets.ViewSet):
    def get_queryset(self, product_id=None):
        queryset = models.ProductImage.objects.order_by("id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def retrieve(self, request, id):
        is_default = request.query_params.get("is_default")

        queryset = self.get_queryset(product_id=id)
        if is_default:
            queryset = queryset.filter(is_default=is_default)
        serializer = serializers.ProductImageSerializer(queryset, many=True)
        return Response(serializer.data, status=200)


class ReviewViewSet(viewsets.ViewSet):
    def get_queryset(self, product_id=None):
        queryset = models.Review.objects.order_by("id")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

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

    def retrieve(self, request, id):
        queryset = self.get_queryset(product_id=id)
        serializer = serializers.OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=200)
