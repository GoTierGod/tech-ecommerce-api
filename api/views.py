from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from . import serializers
from . import models
from . import helpers
from distutils.util import strtobool
from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from django.core.validators import validate_email


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def routes(request):
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
        "/api/customer/update/",
        "/api/customer/create/",
        "/api/customer/delete/",
    ]

    return Response(routes, status=200)


class ProductViewSet(viewsets.ViewSet):
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
            return Response({"message": "Not found"}, status=404)

        serialized_products_data = [
            helpers.compose_product_info(x) for x in page_queryset
        ]

        return Response(serialized_products_data, status=200)

    def retrieve(self, request, id):
        try:
            product = models.Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f'The product with id "{id}" does not exists'}, status=404
            )

        return Response(
            helpers.compose_product_info(product),
            status=200,
        )


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

        page = request.query_params.get("page")
        if page:
            try:
                page = int(page)
            except ValueError:
                page = 1

        if category:
            try:
                queryset = queryset.filter(category__title__iexact=category)
            except ObjectDoesNotExist:
                return Response(
                    {"message": f'Category "{category}" does not exists'}, status=404
                )

        queryset = queryset.extra(select={"discount": "price - offer_price"}).order_by(
            "discount"
        )
        paginator = Paginator(queryset, 10)
        page_queryset = paginator.get_page(page)

        serialized_products_data = [
            helpers.compose_product_info(x) for x in page_queryset
        ]

        return Response(serialized_products_data, status=200)


class BestSellersViewSet(viewsets.ViewSet):
    def list(self, request, category=None):
        queryset = models.Product.objects.all()

        page = request.query_params.get("page")
        if page:
            try:
                page = int(page)
            except ValueError:
                page = 1

        if category:
            try:
                queryset = queryset.filter(category__title__iexact=category)
            except ObjectDoesNotExist:
                return Response(
                    {"message": f'Category "{category}" does not exists'}, status=404
                )

        best_sellers = models.Order.objects.values("product").annotate(
            order_count=Count("id")
        )[:25]

        bs_products = [item["product"] for item in best_sellers]

        queryset = queryset.filter(id__in=bs_products)
        paginator = Paginator(queryset, 10)
        page_queryset = paginator.get_page(page)

        serialized_products_data = [
            helpers.compose_product_info(x) for x in page_queryset
        ]

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
        results = len(queryset)

        order_by_field = request.query_params.get("order_by")
        if order_by_field:
            queryset = queryset.order_by(order_by_field)

        paginator = Paginator(queryset, 10)
        page_queryset = paginator.get_page(page)

        if len(page_queryset) == 0:
            return Response({"message": "Not found"}, status=404)

        serialized_products_data = [
            helpers.compose_product_info(x) for x in page_queryset
        ]

        return Response(
            {
                "results": results,
                "pages": paginator.num_pages,
                "products": serialized_products_data,
                "categories": serialized_categories.data,
                "brands": serialized_brands.data,
            },
            status=200,
        )


class CustomerViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request):
        username = request.user.username

        try:
            customer = models.Customer.objects.get(user__username=username)
            serialized_customer = serializers.CustomerSerializer(customer)
            return Response(serialized_customer.data, status=200)
        except ObjectDoesNotExist:
            return Response({"message": "Not found"}, status=404)

    def create(self, request):
        username = request.data["username"]
        email = request.data["email"]
        password = request.data["password"]
        birthdate = request.data["birthdate"]

        try:
            if models.User.objects.filter(username=username).exists():
                return Response(
                    {"message": f'User with username "{username}" already exists'},
                    status=409,
                )
            validate_email(email)
            if models.User.objects.filter(email=email).exists():
                return Response(
                    {"message": f'The email "{email}" is already being used'},
                    status=409,
                )
            validate_password(password)
            birthdate_date = datetime.strptime(birthdate, "%Y-%m-%d").date()
            if self.calculate_age(birthdate_date) < 18:
                return Response(
                    {"message": "You must be at least 18 years old to register"},
                    status=400,
                )
        except ValidationError as e:
            return Response({"message": e.message}, status=400)

        try:
            new_user = models.User.objects.create_user(
                username=str(username), email=str(email), password=str(password)
            )
            new_customer = models.Customer.objects.create(
                birthdate=birthdate, user=new_user
            )

            new_user.save()
            new_customer.save()
        except Exception:
            return Response({"message": "Something went wrong"}, status=400)

        return Response({"message": "Successfully created"}, status=201)

    def update(self, request):
        try:
            username = request.user.username
            customer = models.Customer.objects.get(user__username=username)
            user = models.User.objects.get(username=username)

            # Update customer data based on request data (if provided)
            new_username = request.data.get("username")
            new_email = request.data.get("email")
            password = request.data.get("password")
            new_password = request.data.get("newpass")
            new_phone = request.data.get("phone")
            new_country = request.data.get("country")
            new_city = request.data.get("city")
            new_address = request.data.get("address")
            new_firstname = request.data.get("firstname")
            new_lastname = request.data.get("lastname")
            new_birthdate = request.data.get("birthdate")
            new_gender = request.data.get("gender")

            if new_email:
                if customer.user.check_password(password):
                    try:
                        if models.User.objects.filter(email=new_email).exists():
                            return Response(
                                {
                                    "message": f'The email "{new_email}" is already being used'
                                },
                                status=409,
                            )
                        validate_email(new_email)
                        user.email = new_email
                    except ValidationError as e:
                        return Response({"message": e.message}, status=400)
                else:
                    return Response({"message": "Incorrect password"}, status=401)

            if new_password:
                if customer.user.check_password(password):
                    try:
                        validate_password(new_password, user=customer.user)
                        user.password = new_password
                    except ValidationError as e:
                        return Response({"message": e.message}, status=400)
                else:
                    return Response({"message": "Incorrect password"}, status=401)

            if new_username:
                if models.User.objects.filter(username=new_username).exists():
                    return Response(
                        {
                            "message": f'User with username "{new_username}" already exists'
                        },
                        status=409,
                    )
                else:
                    user.username = new_username
            if new_phone:
                customer.phone = new_phone
            if new_country:
                customer.country = new_country
            if new_city:
                customer.city = new_city
            if new_address:
                customer.address = new_address
            if new_firstname:
                customer.user.first_name = new_firstname
            if new_lastname:
                customer.user.last_name = new_lastname
            if new_birthdate:
                customer.birthdate = new_birthdate
            if new_gender:
                customer.gender = new_gender

            customer.save()
            user.save()

            return Response({"message": "Updated successfully"}, status=200)
        except:
            return Response({"message": "Something went wrong"}, status=400)

    def delete(self, request):
        try:
            username = request.user.username
            customer = models.Customer.objects.get(user__username=username)
            user = models.User.objects.get(username=username)

            password = request.data["password"]

            if customer.user.check_password(password):
                try:
                    validate_password(password, user=customer.user)
                except ValidationError as e:
                    return Response({"message": e.message}, status=401)
            else:
                return Response({"message": "Incorrect password"}, status=401)

            customer.delete()
            user.delete()

            return Response({"message": "Customer deleted"}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def calculate_age(self, birthdate):
        today = datetime.now().date()
        age = (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )
        return age


class CardItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        cart_items = models.CartItem.objects.filter(customer__user=user)
        serialized_products_data = [
            helpers.compose_product_info(cart_item.product) for cart_item in cart_items
        ]

        return Response(serialized_products_data, status=200)

    def create(self, request, id):
        try:
            user = request.user

            product = models.Product.objects.get(id=id)
            customer = models.Customer.objects.get(user=user)

            new_cart_item = models.CartItem.objects.create(
                product=product, customer=customer
            )

            new_cart_item.save()

            return Response({"message": "The item was added to your cart"}, status=200)
        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def delete(self, request, id):
        try:
            user = request.user

            product = models.Product.objects.get(id=id)
            customer = models.Customer.objects.get(user=user)

            new_cart_item = models.CartItem.objects.get(
                product=product, customer=customer
            )

            new_cart_item.delete()

            return Response(
                {"message": "The item was removed from your cart"}, status=200
            )
        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)


class FavItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        fav_items = models.FavItem.objects.filter(customer__user=user)
        serialized_products_data = [
            helpers.compose_product_info(fav_item.product) for fav_item in fav_items
        ]

        return Response(serialized_products_data, status=200)

    def create(self, request, id):
        try:
            user = request.user

            product = models.Product.objects.get(id=id)
            customer = models.Customer.objects.get(user=user)

            new_fav_item = models.FavItem.objects.create(
                product=product, customer=customer
            )

            new_fav_item.save()

            return Response(
                {"message": "The item was added to your favorites"}, status=200
            )
        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def delete(self, request, id):
        try:
            user = request.user

            product = models.Product.objects.get(id=id)
            customer = models.Customer.objects.get(user=user)

            new_fav_item = models.FavItem.objects.get(
                product=product, customer=customer
            )

            new_fav_item.delete()

            return Response(
                {"message": "The item was removed from your favorites"}, status=200
            )
        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)
