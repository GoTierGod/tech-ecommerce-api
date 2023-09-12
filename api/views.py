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
from . import validators
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
        "purchase/history/<int:id>",
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
            filtered_products = utils.filter_products(products, request)

            paginator = Paginator(filtered_products, 10)
            page_queryset = paginator.get_page(page)

            serialized_products_data = [utils.compose_product(p) for p in page_queryset]

            return Response(serialized_products_data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def retrieve(self, request, product_id):
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

            serialized_products_data = [utils.compose_product(p) for p in page_queryset]

            return Response(serialized_products_data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)


class SearchViewSet(viewsets.ViewSet):
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
                status=200,
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)


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
            return Response({"message": "Something went wrong."}, status=400)

    def create(self, request):
        try:
            username = request.data["username"]
            email = request.data["email"]
            password = request.data["password"]
            birthdate = request.data["birthdate"]

            if len(username) < 8:
                return Response({"message": "Username is too short."}, status=400)
            if len(username) > 16:
                return Response({"message": "Username is too long."}, status=400)
            try:
                validators.profanity_filter(username)
            except ValidationError as e:
                return Response(
                    {"message": "Username was detected as inappropriate."}, status=422
                )
            if models.User.objects.filter(username=username).exists():
                return Response(
                    {"message": f'Username "{username}" is already in use.'},
                    status=409,
                )

            try:
                validate_email(email)
            except ValidationError as e:
                return Response({"message": str(e).capitalize()}, status=400)
            if models.User.objects.filter(email=email).exists():
                return Response(
                    {"message": f'Email "{email}" is already in use.'},
                    status=409,
                )

            try:
                validate_password(password)
            except ValidationError as e:
                return Response({"message": str(e).capitalize()}, status=400)

            birthdate_date = datetime.strptime(birthdate, "%Y-%m-%d").date()
            if self.calculate_age(birthdate_date) < 18:
                return Response(
                    {"message": "You must be at least 18 years old to register."},
                    status=403,
                )

            new_user = models.User.objects.create_user(
                username=username, email=email, password=password
            )
            new_customer = models.Customer.objects.create(
                birthdate=birthdate, user=new_user
            )

            new_user.save()
            new_customer.save()

            return Response({"message": "Account created successfully."}, status=201)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

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
                    if models.User.objects.filter(email=new_email).exists():
                        return Response(
                            {"message": f'Email "{new_email}" is already in use.'},
                            status=409,
                        )
                    try:
                        validate_email(new_email)
                    except ValidationError as e:
                        return Response({"message": str(e).capitalize()}, status=400)
                    user.email = new_email
                else:
                    return Response({"message": "Incorrect password."}, status=401)

            if new_password:
                if customer.user.check_password(password):
                    try:
                        validate_password(new_password)
                    except ValidationError as e:
                        return Response({"message": str(e).capitalize()}, status=400)
                    user.password = new_password
                else:
                    return Response({"message": "Incorrect password."}, status=401)

            if new_username:
                if len(new_username) < 8:
                    return Response({"message": "Username is too short."}, status=400)
                if len(new_username) > 16:
                    return Response({"message": "Username is too long."}, status=400)
                try:
                    validators.profanity_filter(new_username)
                except ValidationError as e:
                    return Response(
                        {"message": "Username was detected as inappropriate."},
                        status=422,
                    )
                if models.User.objects.filter(username=new_username).exists():
                    return Response(
                        {"message": f'Username "{new_username}" is already in use.'},
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
                {"message": "Account information successfully updated."}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def delete(self, request):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            password = request.data["password"]

            if not customer.user.check_password(password):
                return Response({"message": "Incorrect password."}, status=401)

            customer.delete()
            user.delete()

            return Response({"message": "Account successfully deleted."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def list(self, request):
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
                {"likes": likes, "dislikes": dislikes, "reports": reports}, status=200
            )
        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

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
            utils.compose_product(cart_item.product) for cart_item in cart_items
        ]

        return Response(serialized_products_data, status=200)

    def create(self, request, product_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            current_cart_items = models.CartItem.objects.filter(
                customer=customer
            ).count()
            if current_cart_items >= 10:
                return Response(
                    {"message": "You cannot add more than 10 products to your cart."},
                    status=403,
                )

            product = models.Product.objects.get(id=product_id)

            new_cart_item = models.CartItem.objects.create(
                product=product, customer=customer
            )

            new_cart_item.save()

            return Response(
                {"message": "The product was added to your cart."}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def delete(self, request, product_id):
        try:
            user = request.user

            product = models.Product.objects.get(id=product_id)
            customer = models.Customer.objects.get(user=user)

            new_cart_item = models.CartItem.objects.get(
                product=product, customer=customer
            )

            new_cart_item.delete()

            return Response(
                {"message": "The product was removed from your cart."}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def update(self, request, product_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            current_fav_items = models.FavItem.objects.filter(customer=customer).count()
            if current_fav_items >= 25:
                return Response(
                    {
                        "message": "You cannot add more than 25 products to your favorites."
                    },
                    status=403,
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
                {"message": "The product was moved to your favorites."}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)


class FavItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        customer = models.Customer.objects.get(user=user)

        fav_items = models.FavItem.objects.filter(customer=customer)
        serialized_products_data = [
            utils.compose_product(fav_item.product) for fav_item in fav_items
        ]

        return Response(serialized_products_data, status=200)

    def create(self, request, product_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            current_fav_items = models.FavItem.objects.filter(customer=customer).count()
            if current_fav_items >= 25:
                return Response(
                    {
                        "message": "You cannot add more than 25 products to your favorites."
                    },
                    status=403,
                )

            product = models.Product.objects.get(id=product_id)

            new_fav_item = models.FavItem.objects.create(
                product=product, customer=customer
            )

            new_fav_item.save()

            return Response(
                {"message": "The product was added to your favorites."}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def delete(self, request, product_ids=None):
        try:
            user = request.user

            products = models.Product.objects.filter(id__in=product_ids)
            customer = models.Customer.objects.get(user=user)

            fav_items = models.FavItem.objects.filter(
                product__in=products, customer=customer
            )

            fav_items.delete()

            return Response(
                {"message": "The product was removed from your favorites."}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def update(self, request, product_id):
        try:
            user = request.user

            customer = models.Customer.objects.get(user=user)

            current_cart_items = models.CartItem.objects.filter(
                customer=customer
            ).count()
            if current_cart_items >= 10:
                return Response(
                    {"message": "You cannot add more than 10 products to your cart."},
                    status=403,
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
                {"message": "The product was moved to your cart"}, status=200
            )

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)


class PurchaseViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            user = request.user
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
                    quantity=product["quantity"],
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

            return Response({"message": "Order created successfully."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

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
            return Response({"message": "Something went wrong."}, status=400)

    def retrieve(self, request, order_item_id):
        try:
            user = request.user

            customer = models.Customer.objects.get(user=user)
            order_item = models.OrderItem.objects.filter(
                id=order_item_id, customer=customer
            )

            if not order_item.exists():
                return Response(
                    {
                        "message": f'The order item with ID "{order_item_id}" does not exists.'
                    },
                    status=404,
                )
            else:
                order_item = order_item[0]

            serialized_purchase_data = utils.compose_purchase(order_item)

            return Response(serialized_purchase_data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def update(self, request, order_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            order = models.Order.objects.filter(id=order_id, customer=customer)
            if not order.exists():
                return Response(
                    {"message": f'The order with ID "{order_id}" does not exists.'},
                    status=404,
                )
            else:
                order = order[0]

            if order.on_the_way:
                return Response(
                    {"message": "Order on the way, information cannot be modified."},
                    status=403,
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

            return Response({"message": "Order updated successfully."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def delete(self, request, order_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)

            order = models.Order.objects.get(id=order_id)
            order_items = models.OrderItem.objects.filter(
                order=order, customer=customer
            )

            if not order_items.exists():
                return Response("Something went wrong.", status=400)

            if order.dispatched:
                return Response(
                    {"message": "Once dispatched, orders cannot be cancelled."},
                    403,
                )

            order.delete()
            order_items.delete()

            return Response({"message": "Order successfully canceled."}, status=200)

        except Exception as e:
            return Response("Something went wrong.", status=400)


class ReviewViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, product_id):
        try:
            product = models.Product.objects.get(id=product_id)
            reviews = models.Review.objects.filter(product=product)

            serialized_reviews_data = [
                utils.compose_review(review) for review in reviews
            ]

            return Response(serialized_reviews_data, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def create(self, request, product_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=product_id)

            rating = request.data["rating"]
            content = request.data["content"]
            try:
                validators.profanity_filter(content)
            except ValidationError as e:
                return Response(
                    {"message": "Content was detected as inappropriate."}, status=422
                )

            new_review = models.Review.objects.create(
                customer=customer,
                product=product,
                rating=rating,
                content=content,
            )

            new_review.save()

            return Response({"message": "Review created successfully."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def update(self, request, product_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=product_id)

            review = models.Review.objects.get(customer=customer, product=product)

            rating = request.data.ger("rating")
            content = request.data.get("content")

            try:
                validators.profanity_filter(content)
            except ValidationError as e:
                return Response(
                    {"message": "Content was detected as inappropriate."}, status=422
                )

            if rating:
                review.rating = rating
            if content:
                review.content = content

            review.save()

            return Response({"message": "Review sucessfully updated."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def delete(self, request, product_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            product = models.Product.objects.get(id=product_id)

            review = models.Review.objects.get(customer=customer, product=product)

            review.delete()
            return Response({"message": "Review successfully deleted."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def like(self, request, review_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            review = models.Review.objects.get(id=review_id)

            existing_like = models.ReviewLike.objects.filter(
                review=review, customer=customer
            )
            if existing_like.exists():
                existing_like[0].delete()
                return Response({"message": "Like successfully removed."}, status=200)

            existing_dislike = models.ReviewDislike.objects.filter(
                review=review, customer=customer
            )
            if existing_dislike.exists():
                existing_dislike[0].delete()

            models.ReviewLike.objects.create(review=review, customer=customer).save()

            return Response({"message": "Liked."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def dislike(self, request, review_id):
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
                    {"message": "Dislike successfully removed."}, status=200
                )

            existing_like = models.ReviewLike.objects.filter(
                review=review, customer=customer
            )
            if existing_like.exists():
                existing_like[0].delete()

            models.ReviewDislike.objects.create(review=review, customer=customer).save()

            return Response({"message": "Disliked."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)

    def report(self, request, review_id):
        try:
            user = request.user
            customer = models.Customer.objects.get(user=user)
            review = models.Review.objects.get(id=review_id)

            if models.ReviewReport.objects.filter(
                review=review, customer=customer
            ).exists():
                return Response({"message": "Already reported."}, status=403)

            models.ReviewReport.objects.create(review=review, customer=customer).save()

            return Response({"message": "Reported."}, status=200)

        except Exception as e:
            return Response({"message": "Something went wrong."}, status=400)


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
            return Response({"message": "Something went wrong."}, status=400)
