from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Count, Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from . import serializers
from . import models
from . import utils
from distutils.util import strtobool
from datetime import datetime, timedelta

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from django.core.validators import validate_email


@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(["GET"])
def routes(request):
    routes = [
        "products/",
        "products/<int:id>",
        "brands/",
        "categories/",
        "best-sellers/",
        "best-sellers/<str:category>",
        "search/<str:search>",
        "customer/",
        "customer/update/",
        "customer/create/",
        "customer/delete/",
        "cart/",
        "cart/create/<int:id>",
        "cart/delete/<int:id>",
        "cart/move/<int:id>",
        "favorites/",
        "favorites/create/<int:id>",
        "favorites/move/<int:id>",
        "favorites/delete/<intlist:ids>",
        "purchase/",
        "purchase/history/",
        "purchase/update/<int:id>",
        "purchase/delete/<int:id>",
        "reviews/<int:id>",
        "reviews/create/<int:id>",
        "reviews/update/<int:id>",
        "reviews/delete/<int:id>",
    ]

    return Response(routes, status=200)


class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            page = request.query_params.get("page")
            page = int(page) if str(page).isnumeric() else 1

            products = models.Product.objects.all()
            filtered_products = utils.product_filters(products, request)

            paginator = Paginator(filtered_products, 10)
            page_queryset = paginator.get_page(page)

            serialized_products_data = [
                utils.compose_product_info(p) for p in page_queryset
            ]

            return Response(serialized_products_data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def retrieve(self, request, id):
        try:
            product = models.Product.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f'The product with ID "{id}" was not found.'}, status=404
            )

        return Response(
            utils.compose_product_info(product),
            status=200,
        )


class BrandViewSet(viewsets.ViewSet):
    def list(self, request):
        brands = models.Brand.objects.all()
        serialized_brands = serializers.BrandSerializer(brands, many=True)

        return Response(serialized_brands.data, status=200)


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        categories = models.Category.objects.all()
        serialized_categories = serializers.CategorySerializer(categories, many=True)

        return Response(serialized_categories.data, status=200)


class BestSellersViewSet(viewsets.ViewSet):
    def list(self, request, category=None):
        try:
            products = models.Product.objects.all()

            page = request.query_params.get("page")
            page = int(page) if str(page).isnumeric() else 1

            if category:
                products = products.filter(category__title__iexact=category)

            best_sellers = (
                models.OrderItem.objects.values("product")
                .annotate(order_count=Count("id"), total_quantity=Sum("quantity"))
                .order_by("-order_count")[:25]
            )

            best_sellers_products = [item["product"] for item in best_sellers]

            products = products.filter(id__in=best_sellers_products)
            paginator = Paginator(products, 10)
            page_queryset = paginator.get_page(page)

            serialized_products_data = [
                utils.compose_product_info(p) for p in page_queryset
            ]

            return Response(serialized_products_data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)


class SearchProductViewSet(viewsets.ViewSet):
    def list(self, request, search):
        try:
            page = request.query_params.get("page")
            page = int(page) if str(page).isnumeric() else 1

            search_terms = str(search).split(",")

            query = Q()
            for term in search_terms:
                query |= Q(name__icontains=term)
                query |= Q(category__title__icontains=term)
                query |= Q(brand__name__icontains=term)

            products = models.Product.objects.all()
            products = products.filter(query)

            categories = set(p.category for p in products)
            serialized_categories = serializers.CategorySerializer(
                categories, many=True
            )

            brands = set(p.brand for p in products)
            serialized_brands = serializers.BrandSerializer(brands, many=True)

            products = utils.product_filters(products, request)
            results = len(products)

            order_by_field = request.query_params.get("order_by")
            if order_by_field:
                products = products.order_by(order_by_field)

            paginator = Paginator(products, 10)
            page_queryset = paginator.get_page(page)

            serialized_products_data = [
                utils.compose_product_info(p) for p in page_queryset
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

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)


class CustomerViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            serialized_customer = serializers.CustomerSerializer(customer)

            return Response(serialized_customer.data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def create(self, request):
        try:
            username = request.data["username"]
            email = request.data["email"]
            password = request.data["password"]
            birthdate = request.data["birthdate"]

            try:
                if models.User.objects.filter(username=username).exists():
                    return Response(
                        {
                            "message": f'A user with username "{username}" already exists'
                        },
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
                        status=403,
                    )
            except ValidationError as e:
                return Response({"message": e.message}, status=403)

            new_user = models.User.objects.create_user(
                username=username, email=email, password=password
            )
            new_customer = models.Customer.objects.create(
                birthdate=birthdate, user=new_user
            )

            new_user.save()
            new_customer.save()

            return Response(
                {"message": "The customer was successfully created"}, status=201
            )

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def update(self, request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

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
                        return Response({"message": e.message}, status=403)
                else:
                    return Response({"message": "Incorrect password"}, status=401)

            if new_password:
                if customer.user.check_password(password):
                    try:
                        validate_password(new_password)
                        user.password = new_password
                    except ValidationError as e:
                        return Response({"message": e.message}, status=403)
                else:
                    return Response({"message": "Incorrect password"}, status=401)

            if new_username:
                if models.User.objects.filter(username=new_username).exists():
                    return Response(
                        {
                            "message": f'A user with username "{new_username}" already exists'
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

            return Response(
                {"message": "The customer info was pdated successfully"}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def delete(self, request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            password = request.data["password"]

            if not customer.user.check_password(password):
                return Response({"message": "Incorrect password"}, status=401)

            customer.delete()
            user.delete()

            return Response({"message": "The user was deleted"}, status=200)

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
            utils.compose_product_info(cart_item.product) for cart_item in cart_items
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

    def update(self, request, id):
        try:
            user = request.user

            product = models.Product.objects.get(id=id)
            customer = models.Customer.objects.get(user=user)

            new_fav_item = models.FavItem.objects.create(
                product=product, customer=customer
            )

            new_fav_item.save()

            prev_cart_item = models.CartItem.objects.get(
                product=product, customer=customer
            )

            prev_cart_item.delete()

            return Response({"message": "The item was moved to cart"}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)


class FavItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        fav_items = models.FavItem.objects.filter(customer__user=user)
        serialized_products_data = [
            utils.compose_product_info(fav_item.product) for fav_item in fav_items
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

    def delete(self, request, ids=None):
        try:
            user = request.user

            products = models.Product.objects.filter(id__in=ids)
            customer = models.Customer.objects.get(user=user)

            fav_items = models.FavItem.objects.filter(
                product__in=products, customer=customer
            )

            fav_items.delete()

            return Response(
                {"message": "The item was removed from your favorites"}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def update(self, request, id):
        try:
            user = request.user

            product = models.Product.objects.get(id=id)
            customer = models.Customer.objects.get(user=user)

            new_cart_item = models.CartItem.objects.create(
                product=product, customer=customer
            )

            new_cart_item.save()

            prev_fav_item = models.FavItem.objects.get(
                product=product, customer=customer
            )

            prev_fav_item.delete()

            return Response({"message": "The item was moved to cart"}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)


class PurchaseViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            user = request.user

            products = request.data["products"]
            payment_method = request.data["payment_method"]
            country = request.data["country"]
            city = request.data["city"]
            address = request.data["address"]
            notes = request.data["notes"]
            coupon_id = request.data.get("coupon")

            current_date = datetime.now().date()
            delivery_term = current_date + timedelta(days=3)
            delivery_term_str = delivery_term.strftime("%Y-%m-%d")

            order = models.Order.objects.create(
                paid=0,
                payment_method=payment_method,
                delivery_term=delivery_term_str,
                country=country,
                city=city,
                address=address,
                notes=notes,
            )

            customer = models.Customer.objects.get(user=user)

            order_items = [
                models.OrderItem.objects.create(
                    quantity=product["quantity"],
                    customer=customer,
                    product=models.Product.objects.get(id=product["id"]),
                    order=order,
                )
                for product in products
            ]

            total = sum(
                [item.product.offer_price * item.quantity for item in order_items]
            )

            coupon = None
            if str(coupon_id).isdigit():
                coupon = models.Coupon.objects.get(id=coupon_id, customer=customer)
                total = total - coupon.amount

            if len(products) > 1:
                cart_discount = total * len(order_items) / 100
                total = total - cart_discount

            order.paid = total

            order.save()
            [item.save() for item in order_items]
            if coupon:
                coupon.delete()

            return Response({"message": "Order was created successfully"}, status=200)

        except Exception as e:
            print(e)
            return Response({"message": "Something went wrong"}, status=400)

    def list(self, request):
        try:
            user = request.user

            customer = models.Customer.objects.get(user=user)
            order_items = models.OrderItem.objects.filter(customer=customer)

            if not order_items.exists():
                return Response([], status=200)

            serialized_purchases_data = [
                utils.compose_purchase(order_item) for order_item in order_items
            ]

            return Response(serialized_purchases_data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def update(self, request, id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            order = models.Order.objects.get(id=id)
            order_items = models.OrderItem.objects.filter(
                order=order, customer=customer
            )
            if not order_items.exists():
                return Response({"message": "Something went wrong"}, status=400)

            if order.on_the_way:
                return Response(
                    {"message": "Order on the way, information cannot be modified"},
                    status=403,
                )

            country = request.data.get("country")
            city = request.data.get("city")
            address = request.data.get("address")
            notes = request.data.get("notes")
            postal_code = request.data.get("postal_code")

            if country:
                order.country = country
            if city:
                order.city = city
            if address:
                order.address = address
            if notes:
                order.notes = notes
            if postal_code:
                order.postal_code = postal_code

            order.save()

            return Response({"message": "Order updated"}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def delete(self, request, id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            order = models.Order.objects.get(id=id)
            order_items = models.OrderItem.objects.filter(
                order=order, customer=customer
            )

            if not order_items.exists():
                return Response("Something went wrong", status=400)

            if order.dispatched:
                return Response(
                    {"message": "Once dispatched, orders cannot be cancelled"},
                    403,
                )

            order.delete()
            order_items.delete()

            return Response({"message": "Order was canceled"}, status=200)

        except Exception as e:
            return Response("Something went wrong", status=400)


class ReviewViewSet(viewsets.ViewSet):
    def list(self, request, id):
        try:
            product = models.Product.objects.get(id=id)
            reviews = models.Review.objects.filter(product=product)

            serialized_reviews = serializers.ReviewSerializer(reviews, many=True)

            return Response(serialized_reviews.data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def create(self, request, id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=id)

            rating = request.data["rating"]
            title = request.data["title"]
            content = request.data["content"]

            new_review = models.Review.objects.create(
                customer=customer,
                product=product,
                rating=rating,
                title=title,
                content=content,
            )

            new_review.save()

            return Response({"message": "Review created successfully"}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def update(self, request, id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=id)

            review = models.Review.objects.get(customer=customer, product=product)

            rating = request.data.ger("rating")
            title = request.data.get("title")
            content = request.data.get("content")

            if rating:
                review.rating = rating
            if title:
                review.title = title
            if content:
                review.content = content

            review.save()

            return Response({"message": "Review updated sucessfully"}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)

    def delete(self, request, id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=id)

            review = models.Review.objects.get(customer=customer, product=product)

            review.delete()
            return Response({"message": "Review deleted successfully"}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)


class CouponViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            coupons = models.Coupon.objects.filter(customer=customer)
            serialized_coupons = serializers.CouponSerializer(coupons, many=True)

            return Response(serialized_coupons.data, status=200)
        except Exception as e:
            return Response({"message": "Something went wrong"}, status=400)
