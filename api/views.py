from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from . import serializers
from . import models
from . import helpers


# Create your views here.
@api_view()
def welcome(request):
    return Response("Welcome")


class ProductViewSet(viewsets.ViewSet):
    # return less detailed information of a list of products
    def list(self, request):
        # allowed filters to be passed by query parameters
        category = request.query_params.get("category")
        brand = request.query_params.get("brand")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        installments = request.query_params.get("installments")
        stock = request.query_params.get("stock")

        # product queryset
        queryset = models.Product.objects.order_by("id")

        # filter if the allowed query parameters are present
        if category:
            try:
                queryset = queryset.filter(
                    brand_id=models.Category.objects.get(name__iexact=category).id
                )
            except ObjectDoesNotExist:
                return Response(
                    {"message": f"the brand '{brand}' does not exists"},
                    status=404,
                )
        if brand:
            try:
                queryset = queryset.filter(
                    brand_id=models.Brand.objects.get(name__iexact=brand).id
                )
            except ObjectDoesNotExist:
                return Response(
                    {"message": f"the brand '{brand}' does not exists"},
                    status=404,
                )
        if min_price:
            queryset = queryset.filter(offer_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(offer_price__lte=max_price)
        if installments:
            queryset = queryset.filter(installments=installments)
        if stock:
            if stock == "1":
                queryset = queryset.filter(stock__gte=1)
            elif stock == "0":
                queryset = queryset.filter(stock=0)

        # return a response containing the required products
        serialized_products = []
        for product in queryset:
            serialized_products.append(helpers.make_card_product(product))

        return Response(serialized_products, status=200)

    # return a more detailed information about the product with this id
    def retrieve(self, request, id):
        # product
        try:
            product = models.Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"the product with id '{id}' does not exists"}, status=404
            )

        # return a response contained the above data
        return Response(
            helpers.make_detailed_product(product),
            status=200,
        )


class ImageViewSet(viewsets.ViewSet):
    # return all images of the product with this id
    def list(self, request, id):
        try:
            models.Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"the product with id '{id}' does not exists"}, status=404
            )

        queryset = models.ProductImage.objects.order_by("id").filter(product_id=id)

        is_default = request.query_params.get("is_default")
        if is_default:
            queryset = queryset.filter(is_default=is_default)

        serialized = serializers.ProductImageSerializer(queryset, many=True)
        return Response(serialized.data, status=200)


class ReviewViewSet(viewsets.ViewSet):
    # return all reviews of the product with this id
    def list(self, request, id):
        try:
            models.Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"the product with id '{id}' does not exists"}, status=404
            )

        queryset = models.Review.objects.order_by("id").filter(product_id=id)
        serialized = serializers.ReviewSerializer(queryset, many=True)

        return Response(serialized.data, status=200)


class OrderViewSet(viewsets.ViewSet):
    # return all orders of the product with this id
    def list(self, request, id):
        try:
            models.Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"the product with id '{id}' does not exists"}, status=404
            )

        queryset = models.Order.objects.filter(product_id=id).order_by("id")
        serialized = serializers.OrderSerializer(queryset, many=True)

        return Response(serialized.data, status=200)


class BrandViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = models.Brand.objects.order_by("id")
        serialized = serializers.BrandSerializer(queryset, many=True)

        return Response(serialized.data, status=200)


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = models.Category.objects.order_by("id")
        serialized = serializers.CategorySerializer(queryset, many=True)

        return Response(serialized.data, status=200)


class OffersViewSet(viewsets.ViewSet):
    def list(self, request, category=None):
        queryset = models.Product.objects.all()
        if category:
            try:
                queryset = queryset.filter(
                    category=models.Category.objects.get(title__iexact=category).id
                )
            except ObjectDoesNotExist:
                return Response(
                    {"message": f"category '{category}' does not exists"}, status=404
                )

        queryset = queryset.extra(select={"discount": "price - offer_price"}).order_by(
            "discount"
        )

        serialized_products = []
        for product in queryset:
            serialized_products.append(helpers.make_card_product(product))

        return Response(serialized_products, status=200)


class BestSellersViewSet(viewsets.ViewSet):
    def list(self, request, category=None):
        queryset = models.Product.objects.order_by("id")
        if category:
            try:
                queryset = queryset.filter(
                    category=models.Category.objects.get(title__iexact=category).id
                )
            except ObjectDoesNotExist:
                return Response(
                    {"message": f"category '{category}' does not exists"}, status=404
                )

        best_sellers = models.Order.objects.values("product").annotate(
            order_count=Count("id")
        )[:25]

        bs_products = [item["product"] for item in best_sellers]
        queryset = queryset.filter(id__in=bs_products)

        serialized_products = []
        for product in queryset:
            serialized_products.append(helpers.make_card_product(product))

        return Response(serialized_products, status=200)
