from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from . import serializers
from . import models
from . import helpers
from distutils.util import strtobool


# Create your views here.
@api_view(["GET"])
def welcome(request):
    routes = [
        "/api/products/",
        "/api/products/<int:id>",
        "/api/products/images/<int:id>",
        "/api/products/reviews/<int:id>",
        "/api/products/orders/<int:id>",
        "/api/brands/",
        "/api/categories/",
        "/api/offers",
        "/api/offers/<str:category>",
        "/api/search/<str:search>",
        "/api/customer/",
    ]

    return Response(routes, status=200)


class ProductViewSet(viewsets.ViewSet):
    # return a less detailed information of a list of products
    def list(self, request):
        page = request.query_params.get("page")
        if page:
            try:
                page = int(page)
            except ValueError:
                page = 1

        queryset = models.Product.objects.all()
        queryset = helpers.product_filters(queryset, request)

        paginator = Paginator(queryset, 10)
        page_queryset = paginator.get_page(page)

        if len(page_queryset) == 0:
            return Response({"message": "not found"}, status=404)

        serialized_products_data = [helpers.make_card_product(x) for x in page_queryset]

        return Response(serialized_products_data, status=200)

    # return a more detailed information about the product with this id
    def retrieve(self, request, id):
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
        # products presents in the top 25, above
        bs_products = [item["product"] for item in best_sellers]

        # leave only best seller products in our queryset
        queryset = queryset.filter(id__in=bs_products)

        serialized_products_data = [helpers.make_card_product(x) for x in queryset]

        return Response(serialized_products_data, status=200)


class SearchProductViewSet(viewsets.ViewSet):
    def list(self, request, search):
        page = request.query_params.get("page")
        if page:
            try:
                page = int(page)
            except ValueError:
                page = 1

        search_terms = str(search).split(",")

        query = Q()
        for term in search_terms:
            query |= Q(name__icontains=term)
            query |= Q(category__title__icontains=term)
            query |= Q(brand__name__icontains=term)

        queryset = models.Product.objects.all()
        queryset = queryset.filter(query)

        categories = set(x.category for x in queryset)
        serialized_categories = serializers.CategorySerializer(categories, many=True)

        brands = set(x.brand for x in queryset)
        serialized_brands = serializers.BrandSerializer(brands, many=True)

        queryset = helpers.product_filters(queryset, request)

        order_by_field = request.query_params.get("order_by")
        if order_by_field:
            queryset = queryset.order_by(order_by_field)

        paginator = Paginator(queryset, 10)
        page_queryset = paginator.get_page(page)

        if len(page_queryset) == 0:
            return Response({"message": "not found"}, status=404)

        serialized_products_data = [helpers.make_card_product(x) for x in page_queryset]

        return Response(
            {
                "pages": paginator.num_pages,
                "products": serialized_products_data,
                "categories": serialized_categories.data,
                "brands": serialized_brands.data,
            },
            status=200,
        )


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        username = request.data["username"]

        try:
            customer = models.Customer.objects.get(user__username=username)
            serialized_customer = serializers.CustomerSerializer(customer)
            return Response(serialized_customer.data, status=200)
        except ObjectDoesNotExist:
            return Response({"message": "not found"}, status=404)
