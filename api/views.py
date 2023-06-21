from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
from . import serializers
from . import models
from . import helpers
from distutils.util import strtobool


# Create your views here.
@api_view()
def welcome(request):
    return Response("Welcome")


class ProductViewSet(viewsets.ViewSet):
    # return less detailed information of a list of products
    def list(self, request):
        queryset = models.Product.objects.all()

        # allowed filters to be passed as query parameters
        category = request.query_params.get("category")
        brand = request.query_params.get("brand")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        installments = request.query_params.get("installments")
        stock = request.query_params.get("stock")
        is_gamer = request.query_params.get("is_gamer")
        limit = request.query_params.get("limit")

        # filter if the allowed query parameters are present
        if category:
            try:
                queryset = queryset.filter(category__title__iexact=category)
            except ObjectDoesNotExist:
                return Response(
                    {"message": f"the category '{category}' does not exists"},
                    status=404,
                )
        if brand:
            try:
                queryset = queryset.filter(brand__name__iexact=brand)
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
            if strtobool(stock):
                queryset = queryset.filter(stock__gte=1)
            else:
                queryset = queryset.filter(stock=0)
        if is_gamer:
            queryset = queryset.filter(is_gamer=strtobool(is_gamer))
        if limit:
            queryset = queryset[: int(limit)]
        else:
            queryset = queryset[:10]

        serialized_products_data = [helpers.make_card_product(x) for x in queryset]

        return Response(serialized_products_data, status=200)

    # return a more detailed information about the product with this id
    def retrieve(self, request, id):
        # product
        try:
            product = models.Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f"the product with id '{id}' does not exists"}, status=404
            )

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

        queryset = models.ProductImage.objects.all().filter(product_id=id)

        is_default = request.query_params.get("is_default")
        if is_default:
            queryset = queryset.filter(is_default=strtobool(is_default))

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

        queryset = models.Review.objects.all().filter(product_id=id)
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

        queryset = models.Order.objects.filter(product_id=id).all()
        serialized = serializers.OrderSerializer(queryset, many=True)

        return Response(serialized.data, status=200)


class BrandViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = models.Brand.objects.all()
        serialized = serializers.BrandSerializer(queryset, many=True)

        return Response(serialized.data, status=200)


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = models.Category.objects.all()
        serialized = serializers.CategorySerializer(queryset, many=True)

        return Response(serialized.data, status=200)


class OffersViewSet(viewsets.ViewSet):
    def list(self, request, category=None):
        queryset = models.Product.objects.all()

        limit = request.query_params.get("limit")

        if category:
            try:
                queryset = queryset.filter(category__title__iexact=category)
            except ObjectDoesNotExist:
                return Response(
                    {"message": f"category '{category}' does not exists"}, status=404
                )

        # sort products by amount discounted in descending order
        queryset = queryset.extra(select={"discount": "price - offer_price"}).order_by(
            "discount"
        )[: int(limit) if limit else 10]

        serialized_products_data = [helpers.make_card_product(x) for x in queryset]

        return Response(serialized_products_data, status=200)


class BestSellersViewSet(viewsets.ViewSet):
    def list(self, request, category=None):
        queryset = models.Product.objects.all()

        if category:
            try:
                queryset = queryset.filter(category__title__iexact=category)
            except ObjectDoesNotExist:
                return Response(
                    {"message": f"category '{category}' does not exists"}, status=404
                )

        # top 25 best seller products grouping orders by product ID
        best_sellers = models.Order.objects.values("product").annotate(
            order_count=Count("id")
        )[:25]
        # products presents in the top 25 best sellers products
        bs_products = [item["product"] for item in best_sellers]

        # leave only best seller products in our queryset
        queryset = queryset.filter(id__in=bs_products)

        serialized_products_data = [helpers.make_card_product(x) for x in queryset]

        return Response(serialized_products_data, status=200)


class SearchViewSet(viewsets.ViewSet):
    def list(self, request, search):
        search_terms = str(search).split(",")

        # create three searchs per each search term
        query = Q()
        for term in search_terms:
            query |= Q(name__icontains=term)
            query |= Q(category__title__icontains=term)
            query |= Q(brand__name__icontains=term)

        queryset = models.Product.objects.filter(query)[:10]

        serialized_products_data = [helpers.make_card_product(x) for x in queryset]

        return Response(serialized_products_data, status=200)
