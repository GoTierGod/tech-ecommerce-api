# Django
from django.db.models import Count, Q, Sum
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

# REST Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.request import Request

# App
from . import serializers
from . import models
from . import utils
from . import validators

# Caching
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Validation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Other
from datetime import datetime, timedelta, date


@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(["GET"])
def routes(request: Request):
    return Response({"message": "Made by @GoTierGod."}, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60 * 60))
    def list(self, request: Request):
        try:
            page = request.query_params.get("page")
            page = int(page) if str(page).isnumeric() else 1

            products = models.Product.objects.all()
            filtered_products = utils.filter_products(products, request)

            paginator = Paginator(filtered_products, 10)
            page_queryset = paginator.get_page(page)

            serialized_products_data = [utils.compose_product(p) for p in page_queryset]

            return Response(serialized_products_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request: Request, product_id: int):
        try:
            product = models.Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response(
                {"message": f'Product with ID "{product_id}" does not exists.'},
                status=404,
            )

        return Response(
            utils.compose_product(product),
            status=200,
        )


class BrandViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request: Request):
        brands = models.Brand.objects.all()
        serialized_brands = serializers.BrandSerializer(brands, many=True)

        return Response(serialized_brands.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request: Request):
        categories = models.Category.objects.all()
        serialized_categories = serializers.CategorySerializer(categories, many=True)

        return Response(serialized_categories.data, status=status.HTTP_200_OK)


class SearchViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60 * 60 * 1))
    def list(self, request: Request, search: str):
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

            installments = set(p.installments for p in products)

            products = utils.filter_products(products, request)
            results = len(products)

            order_by_field = request.query_params.get("order_by")
            if order_by_field:
                products = products.order_by(order_by_field)

            paginator = Paginator(products, 10)
            page_queryset = paginator.get_page(page)

            serialized_products_data = [utils.compose_product(p) for p in page_queryset]

            return Response(
                {
                    "results": results,
                    "pages": paginator.num_pages,
                    "products": serialized_products_data,
                    "categories": serialized_categories.data,
                    "brands": serialized_brands.data,
                    "installments": installments,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )


class CustomerViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @method_decorator(cache_page(60))
    def retrieve(self, request: Request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            serialized_customer_data = utils.compose_customer(customer)

            return Response(serialized_customer_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request: Request):
        try:
            username = request.data["username"]
            email = request.data["email"]
            password = request.data["password"]
            birthdate = request.data["birthdate"]

            # Given my database limitations, i need to control the database size :3
            customers_created_today = models.User.objects.filter(
                date_joined=date.today()
            ).count()
            if customers_created_today >= 50:
                return Response(
                    {
                        "message": "The app has reached its daily account creation limit."
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            if len(username) < 8:
                return Response(
                    {"message": "Username is too short."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if len(username) > 16:
                return Response(
                    {"message": "Username is too long."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                validators.profanity_filter(username)
            except ValidationError as e:
                return Response(
                    {"message": "Username was detected as inappropriate."},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            if models.User.objects.filter(username=username).exists():
                return Response(
                    {"message": f'Username "{username}" is already in use.'},
                    status=status.HTTP_409_CONFLICT,
                )

            try:
                validate_email(email)
            except ValidationError as e:
                return Response({"message": str(e).capitalize()}, status=400)
            if models.User.objects.filter(email=email).exists():
                return Response(
                    {"message": f'Email "{email}" is already in use.'},
                    status=status.HTTP_409_CONFLICT,
                )

            try:
                validate_password(password)
            except ValidationError as e:
                return Response({"message": str(e).capitalize()}, status=400)

            birthdate_date = datetime.strptime(birthdate, "%Y-%m-%d").date()
            if self.calculate_age(birthdate_date) < 18:
                return Response(
                    {"message": "You must be at least 18 years old to register."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            new_user = models.User.objects.create_user(
                username=username, email=email, password=password
            )
            new_customer = models.Customer.objects.create(
                birthdate=birthdate, user=new_user
            )

            new_user.save()
            new_customer.save()

            return Response(
                {"message": "Account created successfully."},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request: Request):
        try:
            user: models.User = request.user
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
                if user.check_password(password):
                    if models.User.objects.filter(email=new_email).exists():
                        return Response(
                            {"message": f'Email "{new_email}" is already in use.'},
                            status=status.HTTP_409_CONFLICT,
                        )
                    try:
                        validate_email(new_email)
                    except ValidationError as e:
                        return Response(
                            {"message": str(e).capitalize()},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    user.email = new_email
                else:
                    return Response(
                        {"message": "Incorrect password."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

            if new_password:
                if user.check_password(password):
                    try:
                        validate_password(new_password)
                    except ValidationError as e:
                        return Response(
                            {"message": str(e).capitalize()},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    user.password = new_password
                else:
                    return Response(
                        {"message": "Incorrect password."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

            if new_username:
                if len(new_username) < 8:
                    return Response(
                        {"message": "Username is too short."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if len(new_username) > 16:
                    return Response(
                        {"message": "Username is too long."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                try:
                    validators.profanity_filter(new_username)
                except ValidationError as e:
                    return Response(
                        {"message": "Username was detected as inappropriate."},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )
                if models.User.objects.filter(username=new_username).exists():
                    return Response(
                        {"message": f'Username "{new_username}" is already in use.'},
                        status=status.HTTP_409_CONFLICT,
                    )
                else:
                    user.username = new_username

            if new_birthdate:
                new_birthdate_date = datetime.strptime(new_birthdate, "%Y-%m-%d").date()
                if self.calculate_age(new_birthdate_date) < 18:
                    return Response(
                        {"message": "You must be at least 18 years old to register."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                else:
                    customer.birthdate = new_birthdate

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
            if new_gender:
                customer.gender = new_gender

            customer.save()
            user.save()

            return Response(
                {"message": "Account information successfully updated."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request):
        try:
            user: models.User = request.user
            customer = models.Customer.objects.get(user=user)

            password = request.data["password"]

            if not user.check_password(password):
                return Response(
                    {"message": "Incorrect password."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            customer.delete()
            user.delete()

            return Response(
                {"message": "Account successfully deleted."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request: Request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            likes = [
                like.review.id
                for like in models.ReviewLike.objects.filter(customer=customer)
            ]
            dislikes = [
                dislike.review.id
                for dislike in models.ReviewDislike.objects.filter(customer=customer)
            ]
            reports = [
                report.review.id
                for report in models.ReviewReport.objects.filter(customer=customer)
            ]

            return Response(
                {"likes": likes, "dislikes": dislikes, "reports": reports},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def calculate_age(self, birthdate) -> int:
        today = datetime.now().date()
        age = (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )
        return age


class CartItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request: Request):
        user = request.user

        cart_items = models.CartItem.objects.filter(customer__user=user)
        serialized_products_data = [
            utils.compose_product(cart_item.product) for cart_item in cart_items
        ]

        return Response(serialized_products_data, status=status.HTTP_200_OK)

    def create(self, request: Request, product_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            current_cart_items = models.CartItem.objects.filter(
                customer=customer
            ).count()
            if current_cart_items >= 10:
                return Response(
                    {"message": "You cannot add more than 10 products to your cart."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            product = models.Product.objects.get(id=product_id)

            new_cart_item = models.CartItem.objects.create(
                product=product, customer=customer
            )

            new_cart_item.save()

            return Response(
                {"message": "The product was added to your cart."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, product_id: int):
        try:
            user = request.user

            product = models.Product.objects.get(id=product_id)
            customer = models.Customer.objects.get(user=user)

            new_cart_item = models.CartItem.objects.get(
                product=product, customer=customer
            )

            new_cart_item.delete()

            return Response(
                {"message": "The product was removed from your cart."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request: Request, product_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            current_fav_items = models.FavItem.objects.filter(customer=customer).count()
            if current_fav_items >= 25:
                return Response(
                    {
                        "message": "You cannot add more than 25 products to your favorites."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            product = models.Product.objects.get(id=product_id)

            new_fav_item = models.FavItem.objects.create(
                product=product, customer=customer
            )

            new_fav_item.save()

            prev_cart_item = models.CartItem.objects.get(
                product=product, customer=customer
            )

            prev_cart_item.delete()

            return Response(
                {"message": "The product was moved to your favorites."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )


class FavItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request: Request):
        user = request.user
        customer = models.Customer.objects.get(user=user)

        fav_items = models.FavItem.objects.filter(customer=customer)
        serialized_products_data = [
            utils.compose_product(fav_item.product) for fav_item in fav_items
        ]

        return Response(serialized_products_data, status=status.HTTP_200_OK)

    def create(self, request: Request, product_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            current_fav_items = models.FavItem.objects.filter(customer=customer).count()
            if current_fav_items >= 25:
                return Response(
                    {
                        "message": "You cannot add more than 25 products to your favorites."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            product = models.Product.objects.get(id=product_id)

            new_fav_item = models.FavItem.objects.create(
                product=product, customer=customer
            )

            new_fav_item.save()

            return Response(
                {"message": "The product was added to your favorites."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, product_ids=None):
        try:
            user = request.user

            products = models.Product.objects.filter(id__in=product_ids)
            customer = models.Customer.objects.get(user=user)

            fav_items = models.FavItem.objects.filter(
                product__in=products, customer=customer
            )

            fav_items.delete()

            return Response(
                {"message": "The product was removed from your favorites."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request: Request, product_id: int):
        try:
            user = request.user

            customer = models.Customer.objects.get(user=user)

            current_cart_items = models.CartItem.objects.filter(
                customer=customer
            ).count()
            if current_cart_items >= 10:
                return Response(
                    {"message": "You cannot add more than 10 products to your cart."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            product = models.Product.objects.get(id=product_id)

            new_cart_item = models.CartItem.objects.create(
                product=product, customer=customer
            )

            new_cart_item.save()

            prev_fav_item = models.FavItem.objects.get(
                product=product, customer=customer
            )

            prev_fav_item.delete()

            return Response(
                {"message": "The product was moved to your cart"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )


class PurchaseViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request: Request):
        try:
            user: models.User = request.user
            customer = models.Customer.objects.get(user=user)

            current_active_orders = models.Order.objects.filter(
                customer=customer, delivered=False
            ).count()
            if current_active_orders >= 3:
                return Response(
                    {"message": "You cannot have more than 3 active orders."},
                    status=403,
                )

            products = request.data["products"]
            payment_method = request.data["payment_method"]
            country = request.data["country"]
            city = request.data["city"]
            address = request.data["address"]
            notes = request.data["notes"]
            coupon_id = request.data.get("coupon")

            # Given my database limitations, i need to control the database size :3
            orders_created_today = models.Order.objects.filter(
                purchase_date=date.today()
            ).count()
            if orders_created_today >= 100:
                return Response(
                    {"message": "The app has reached its daily order creation limit."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

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
                customer=customer,
            )

            order_items = [
                models.OrderItem.objects.create(
                    quantity=int(product["quantity"]),
                    product=models.Product.objects.get(id=int(product["id"])),
                    order=order,
                )
                for product in products
            ]

            total = sum(
                [item.product.offer_price * item.quantity for item in order_items]
            )

            coupon = None
            if coupon_id:
                if str(coupon_id).isdigit():
                    coupon = models.Coupon.objects.get(
                        id=int(coupon_id), customer=customer
                    )
                    total = total - coupon.amount

            if len(products) > 1:
                cart_discount = total * len(order_items) / 100
                total = total - cart_discount

            order.paid = total

            order.save()
            [item.save() for item in order_items]
            if coupon:
                coupon.delete()

            return Response(
                {"message": "Order created successfully."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request: Request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            order = models.Order.objects.filter(customer=customer)
            if not order.exists():
                return Response([], status=status.HTTP_200_OK)
            else:
                order = order[0]

            order_items = models.OrderItem.objects.filter(order=order)

            serialized_purchases_data = [
                utils.compose_purchase(order_item) for order_item in order_items
            ]

            return Response(serialized_purchases_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request: Request, order_item_id: int):
        try:
            user = request.user

            customer = models.Customer.objects.get(user=user)
            orders = models.Order.objects.filter(customer=customer)
            if not orders.exists():
                return Response(
                    {
                        "message": f'The order item with ID "{order_item_id}" does not exists.'
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            order_item = models.OrderItem.objects.filter(
                id=order_item_id, order__in=orders
            )

            if not order_item.exists():
                return Response(
                    {
                        "message": f'The order item with ID "{order_item_id}" does not exists.'
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                order_item = order_item[0]

            serialized_purchase_data = utils.compose_purchase(order_item)

            return Response(serialized_purchase_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request: Request, order_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            order = models.Order.objects.filter(id=order_id, customer=customer)
            if not order.exists():
                return Response(
                    {"message": f'The order with ID "{order_id}" does not exists.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                order = order[0]

            if order.on_the_way:
                return Response(
                    {"message": "Order on the way, information cannot be modified."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            country = request.data.get("country")
            city = request.data.get("city")
            address = request.data.get("address")
            notes = request.data.get("notes")

            if country:
                order.country = country
            if city:
                order.city = city
            if address:
                order.address = address
            if notes:
                order.notes = notes

            order.save()

            return Response(
                {"message": "Order updated successfully."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, order_id: int):
        try:
            user: models.User = request.user
            customer = models.Customer.objects.get(user=user)

            order = models.Order.objects.get(id=order_id, customer=customer)
            order_items = models.OrderItem.objects.filter(order=order)

            if not order_items.exists():
                return Response(
                    "Something went wrong.", status=status.HTTP_400_BAD_REQUEST
                )

            if order.dispatched:
                return Response(
                    {"message": "Once dispatched, orders cannot be cancelled."},
                    403,
                )

            order.delete()
            order_items.delete()

            return Response(
                {"message": "Order successfully canceled."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response("Something went wrong.", status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @method_decorator(cache_page(60 * 60))
    def list(self, request: Request, product_id: int):
        try:
            product = models.Product.objects.get(id=product_id)
            reviews = models.Review.objects.filter(product=product, hidden=False)

            serialized_reviews_data = [
                utils.compose_review(review) for review in reviews
            ]

            return Response(serialized_reviews_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request: Request, product_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=product_id)

            rating = request.data["rating"]
            content = request.data["content"]

            # Given my database limitations, i need to control the database size :3
            reviews_created_today = models.Review.objects.filter(
                date=date.today()
            ).count()
            if reviews_created_today >= 100:
                return Response(
                    {"message": "The app has reached its daily review creation limit."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            try:
                validators.profanity_filter(content)
            except ValidationError as e:
                return Response(
                    {"message": "Content was detected as inappropriate."},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            new_review = models.Review.objects.create(
                customer=customer,
                product=product,
                rating=rating,
                content=content,
            )

            new_review.save()

            return Response(
                {"message": "Review created successfully."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request: Request, product_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=product_id)

            review = models.Review.objects.get(customer=customer, product=product)

            rating = request.data.get("rating")
            content = request.data.get("content")

            try:
                validators.profanity_filter(content)
            except ValidationError as e:
                return Response(
                    {"message": "Content was detected as inappropriate."},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            if rating:
                review.rating = rating
            if content:
                review.content = content

            review.save()

            return Response(
                {"message": "Review sucessfully updated."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request: Request, product_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=product_id)

            review = models.Review.objects.get(customer=customer, product=product)

            review.delete()
            return Response(
                {"message": "Review successfully deleted."}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def like(self, request: Request, review_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            review = models.Review.objects.get(id=review_id)

            existing_like = models.ReviewLike.objects.filter(
                review=review, customer=customer
            )
            if existing_like.exists():
                existing_like[0].delete()
                return Response(
                    {"message": "Like successfully removed."}, status=status.HTTP_200_OK
                )

            existing_dislike = models.ReviewDislike.objects.filter(
                review=review, customer=customer
            )
            if existing_dislike.exists():
                existing_dislike[0].delete()

            models.ReviewLike.objects.create(review=review, customer=customer).save()

            return Response({"message": "Liked."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def dislike(self, request: Request, review_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            review = models.Review.objects.get(id=review_id)

            existing_dislike = models.ReviewDislike.objects.filter(
                review=review, customer=customer
            )
            if existing_dislike.exists():
                existing_dislike[0].delete()
                return Response(
                    {"message": "Dislike successfully removed."},
                    status=status.HTTP_200_OK,
                )

            existing_like = models.ReviewLike.objects.filter(
                review=review, customer=customer
            )
            if existing_like.exists():
                existing_like[0].delete()

            models.ReviewDislike.objects.create(review=review, customer=customer).save()

            return Response({"message": "Disliked."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )

    def report(self, request: Request, review_id: int):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            review = models.Review.objects.get(id=review_id)

            if models.ReviewReport.objects.filter(
                review=review, customer=customer
            ).exists():
                return Response(
                    {"message": "Already reported."}, status=status.HTTP_403_FORBIDDEN
                )

            models.ReviewReport.objects.create(review=review, customer=customer).save()

            return Response({"message": "Reported."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )


class CouponViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60))
    def list(self, request: Request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            coupons = models.Coupon.objects.filter(customer=customer)
            serialized_coupons = serializers.CouponSerializer(coupons, many=True)

            return Response(serialized_coupons.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST
            )
