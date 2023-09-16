from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from django.urls import reverse
from django.contrib.auth.hashers import make_password

import json

from . import models
from . import utils
from . import serializers


# Create your tests here.
class ProductTest(APITestCase):
    def setUp(self):
        self.brand = models.Brand.objects.create(
            name="Motorola",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.category = models.Category.objects.create(
            title="Smartphones", description="Description", icon="Icon"
        )

        self.product = models.Product.objects.create(
            id=2,
            name="Motorola G22",
            description="Description",
            price="199.00",
            offer_price="149.00",
            installments=6,
            stock=100,
            months_warranty=12,
            is_gamer=False,
            brand=self.brand,
            category=self.category,
        )

        self.product_image = models.ProductImage.objects.create(
            url="URL",
            description="Motorola G22",
            product=self.product,
            is_default=True,
        )

    def test_list_products(self):
        """
        Ensure anyone can list available products
        """
        url = reverse("product-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [utils.compose_product(self.product)],
            msg="Incorrect format of products information",
        )

    def test_retrieve_products(self):
        """
        Ensure anyone can retrieve a specific product by its ID
        """
        url = reverse("product-retrieve", kwargs={"product_id": 2})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            utils.compose_product(self.product),
            msg="Incorrect format of product information",
        )


class BrandAndCategoryTest(APITestCase):
    def setUp(self):
        self.brand = models.Brand.objects.create(
            name="HP",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.category = models.Category.objects.create(
            title="Laptops", description="Description", icon="Icon"
        )

    def test_list_brands(self):
        """
        Ensure anyone can list available brands
        """
        url = reverse("brand-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            serializers.BrandSerializer(models.Brand.objects.all(), many=True).data,
            msg="Incorrect format of serialized brands data",
        )

    def test_list_categories(self):
        """
        Ensure anyone can list available categories
        """
        url = reverse("category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            serializers.CategorySerializer(
                models.Category.objects.all(), many=True
            ).data,
            msg="Incorrect format of serialized categories data",
        )


class SearchTest(APITestCase):
    def setUp(self):
        self.brand_1 = models.Brand.objects.create(
            name="HP",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.brand_2 = models.Brand.objects.create(
            name="Samsung",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.category_1 = models.Category.objects.create(
            title="Laptops", description="Description", icon="Icon"
        )

        self.category_2 = models.Category.objects.create(
            title="Smartphones", description="Description", icon="Icon"
        )

        self.product_1 = models.Product.objects.create(
            id=1,
            name="HP Victus 15",
            description="Description",
            price="849.00",
            offer_price="749.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_2 = models.Product.objects.create(
            id=2,
            name="HP Victus 16",
            description="Description",
            price="1099.00",
            offer_price="949.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_3 = models.Product.objects.create(
            id=3,
            name="Samsung S22",
            description="Description",
            price="1099.00",
            offer_price="949.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_2,
            category=self.category_2,
        )

        self.product_image_1 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 15",
            product=self.product_1,
            is_default=True,
        )

        self.product_image_2 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 16",
            product=self.product_2,
            is_default=True,
        )

        self.product_image_3 = models.ProductImage.objects.create(
            url="URL",
            description="Samsung S22",
            product=self.product_3,
            is_default=True,
        )

    def test_search(self):
        """
        Ensure anyone can search for products and get the correct response
        """
        products = [self.product_1, self.product_2]
        serialized_products_data = [utils.compose_product(p) for p in products]
        categories = set(p.category for p in products)
        serialized_categories = serializers.CategorySerializer(categories, many=True)
        brands = set(p.brand for p in products)
        serialized_brands = serializers.BrandSerializer(brands, many=True)
        installments = set(p.installments for p in products)

        url = reverse("search-list", kwargs={"search": "lap"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "results": len(products),
                "pages": 1,
                "products": serialized_products_data,
                "categories": serialized_categories.data,
                "brands": serialized_brands.data,
                "installments": installments,
            },
            msg="Incorrect format of search response",
        )


class CustomerTest(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create(
            username="gotiergod",
            email="gotiergod@gmail.com",
            password=make_password("ADaska#$99"),
        )

        self.customer = models.Customer.objects.create(
            birthdate="2000-02-02",
            gender="M",
            phone="Phone",
            country="Country",
            city="City",
            address="Address",
            points=6,
            user=self.user,
        )

        access_token = AccessToken.for_user(self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

    def test_create_customer(self):
        """
        Ensure anyone can create a new account
        """
        data = {
            "username": "newuser30yo",
            "email": "newuser@gmail.com",
            "password": "NUpass#3011",
            "birthdate": "2001-04-11",
        }

        url = reverse("customer-create")
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            models.Customer.objects.filter(user__username="newuser30yo").exists(),
            msg="The customer was not created correctly",
        )

    def test_retrieve_customer(self):
        """
        Ensure customers can retrieve their account information
        """

        url = reverse("customer-retrieve")
        response = self.client.get(
            url,
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            utils.compose_customer(self.customer),
            msg="Incorrect format of customer information",
        )

    def test_update_customer(self):
        """
        Ensure customers can update their account information
        """
        data = {
            "username": "godtiergo",
            "email": "ivan@gmail.com",
            "firstname": "Iván",
            "country": "Chile",
            "password": "ADaska#$99",
        }

        url = reverse("customer-update")
        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            models.Customer.objects.filter(user__username="godtiergo").exists(),
            msg="The customer was not updated correctly",
        )

    def test_delete_customer(self):
        """
        Ensure customers can delete their accounts
        """
        url = reverse("customer-delete")
        response = self.client.delete(
            url, data={"password": "ADaska#$99"}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            models.Customer.objects.filter(user=self.customer.user).exists(),
            msg="The customer was not deleted",
        )

    def test_list_customer_interactions(self):
        """
        Ensure customer can list their interactions which corresponds to
        likes, dislikes and reports made on reviews
        """
        url = reverse("customer-list")
        response = self.client.get(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"likes": [], "dislikes": [], "reports": []},
            msg="Incorrect format of customer interactions",
        )


class CartTest(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create(
            username="gotiergod",
            email="gotiergod@gmail.com",
            password=make_password("ADaska#$99"),
        )

        self.customer = models.Customer.objects.create(
            birthdate="2000-02-02",
            gender="M",
            phone="Phone",
            country="Country",
            city="City",
            address="Address",
            points=6,
            user=self.user,
        )

        self.brand_1 = models.Brand.objects.create(
            name="HP",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.brand_2 = models.Brand.objects.create(
            name="Samsung",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.category_1 = models.Category.objects.create(
            title="Laptops", description="Description", icon="Icon"
        )

        self.category_2 = models.Category.objects.create(
            title="Smartphones", description="Description", icon="Icon"
        )

        self.product_1 = models.Product.objects.create(
            id=1,
            name="HP Victus 15",
            description="Description",
            price="849.00",
            offer_price="749.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_2 = models.Product.objects.create(
            id=2,
            name="HP Victus 16",
            description="Description",
            price="1099.00",
            offer_price="949.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_image_1 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 15",
            product=self.product_1,
            is_default=True,
        )

        self.product_image_2 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 16",
            product=self.product_2,
            is_default=True,
        )

        self.cart_item_1 = models.CartItem.objects.create(
            product=self.product_1, customer=self.customer
        )

        access_token = AccessToken.for_user(self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

    def test_list_cart_items(self):
        """
        Ensure customers can list their cart items
        """
        url = reverse("cart-list")
        response = self.client.get(url, **self.headers)

        cart_items = models.CartItem.objects.filter(customer=self.customer)
        serialized_products_data = [
            utils.compose_product(item.product) for item in cart_items
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, serialized_products_data, msg="Incorrect list of cart items"
        )

    def test_create_cart_items(self):
        """
        Ensure customers can add new cart items
        """
        url = reverse("cart-create", kwargs={"product_id": 2})
        response = self.client.post(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            models.CartItem.objects.filter(product__id=2).exists(),
            msg="The cart item was not added",
        )

    def test_move_cart_items_to_favs(self):
        """
        Ensure customers can move their cart items to favorites
        """
        url = reverse("cart-update", kwargs={"product_id": 1})
        response = self.client.patch(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            models.CartItem.objects.filter(product__id=1).exists(),
            msg="The cart iten was not removed",
        )
        self.assertTrue(
            models.FavItem.objects.filter(product__id=1).exists(),
            msg="The cart item was not moved",
        )

    def test_delete_cart_items(self):
        """
        Ensure customers can remove their cart items
        """
        url = reverse("cart-delete", kwargs={"product_id": 1})
        response = self.client.delete(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            models.CartItem.objects.filter(product__id=1).exists(),
            msg="The cart item was not removed",
        )


class FavoritesTest(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create(
            username="gotiergod",
            email="gotiergod@gmail.com",
            password=make_password("ADaska#$99"),
        )

        self.customer = models.Customer.objects.create(
            birthdate="2000-02-02",
            gender="M",
            phone="Phone",
            country="Country",
            city="City",
            address="Address",
            points=6,
            user=self.user,
        )

        self.brand_1 = models.Brand.objects.create(
            name="HP",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.brand_2 = models.Brand.objects.create(
            name="Samsung",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.category_1 = models.Category.objects.create(
            title="Laptops", description="Description", icon="Icon"
        )

        self.category_2 = models.Category.objects.create(
            title="Smartphones", description="Description", icon="Icon"
        )

        self.product_1 = models.Product.objects.create(
            id=1,
            name="HP Victus 15",
            description="Description",
            price="849.00",
            offer_price="749.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_2 = models.Product.objects.create(
            id=2,
            name="HP Victus 16",
            description="Description",
            price="1099.00",
            offer_price="949.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_image_1 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 15",
            product=self.product_1,
            is_default=True,
        )

        self.product_image_2 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 16",
            product=self.product_2,
            is_default=True,
        )

        self.cart_item_1 = models.FavItem.objects.create(
            product=self.product_1, customer=self.customer
        )

        access_token = AccessToken.for_user(self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

    def test_list_favorites(self):
        """
        Ensure customers can list their favorites
        """
        url = reverse("favorites-list")
        response = self.client.get(url, **self.headers)

        fav_items = models.FavItem.objects.filter(customer=self.customer)
        serialized_products_data = [
            utils.compose_product(item.product) for item in fav_items
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, serialized_products_data, msg="Incorrect list of favorites"
        )

    def test_create_favorites(self):
        """
        Ensure customers can add new favorites
        """
        url = reverse("favorites-create", kwargs={"product_id": 2})
        response = self.client.post(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            models.FavItem.objects.filter(product__id=2).exists(),
            msg="The favorite was not added",
        )

    def test_move_favs_to_cart(self):
        """
        Ensure customers can move their favorites to cart
        """
        url = reverse("favorites-update", kwargs={"product_id": 1})
        response = self.client.patch(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            models.FavItem.objects.filter(product__id=1).exists(),
            msg="The favorite was not removed",
        )
        self.assertTrue(
            models.CartItem.objects.filter(product__id=1).exists(),
            msg="The favorite was not moved",
        )

    def test_delete_favorites(self):
        """
        Ensure customers can remove their favorites
        """
        url = reverse("favorites-delete", kwargs={"product_ids": [1]})
        response = self.client.delete(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            models.FavItem.objects.filter(product__id=1).exists(),
            msg="The favorite was not removed",
        )


class PurchaseTest(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create(
            username="gotiergod",
            email="gotiergod@gmail.com",
            password=make_password("ADaska#$99"),
        )

        self.customer = models.Customer.objects.create(
            birthdate="2000-02-02",
            gender="M",
            phone="Phone",
            country="Country",
            city="City",
            address="Address",
            points=6,
            user=self.user,
        )

        self.brand_1 = models.Brand.objects.create(
            name="HP",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.brand_2 = models.Brand.objects.create(
            name="Samsung",
            description="Description",
            website_url="URL",
            logo_url="Logo",
        )

        self.category_1 = models.Category.objects.create(
            title="Laptops", description="Description", icon="Icon"
        )

        self.category_2 = models.Category.objects.create(
            title="Smartphones", description="Description", icon="Icon"
        )

        self.product_1 = models.Product.objects.create(
            id=1,
            name="HP Victus 15",
            description="Description",
            price="849.00",
            offer_price="749.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_2 = models.Product.objects.create(
            id=2,
            name="HP Victus 16",
            description="Description",
            price="1099.00",
            offer_price="949.00",
            installments=12,
            stock=50,
            months_warranty=24,
            is_gamer=True,
            brand=self.brand_1,
            category=self.category_1,
        )

        self.product_image_1 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 15",
            product=self.product_1,
            is_default=True,
        )

        self.product_image_2 = models.ProductImage.objects.create(
            url="URL",
            description="HP Victus 16",
            product=self.product_2,
            is_default=True,
        )

        self.coupon = models.Coupon.objects.create(
            title="Global Offer", amount="100.00", customer=self.customer
        )

        self.order = models.Order.objects.create(
            paid=self.product_1.offer_price,
            payment_method="Mastercard",
            delivery_term="2023-09-12",
            country=self.customer.country,
            city=self.customer.city,
            address=self.customer.address,
            notes="Nothing",
            customer=self.customer,
        )

        self.order_item = models.OrderItem.objects.create(
            quantity=1, product=self.product_1, order=self.order
        )

        access_token = AccessToken.for_user(self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

    def test_create_purchase(self):
        """
        Ensure customers can purchase products
        """
        data = {
            "products": [
                {"id": self.product_1.pk, "quantity": 2},
                {"id": self.product_2.pk, "quantity": 1},
            ],
            "payment_method": "Visa",
            "country": "Country",
            "city": "City",
            "address": "Address",
            "notes": "Nothing",
            "coupon": self.coupon.pk,
        }

        url = reverse("purchase-create")
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            models.Order.objects.all().count(),
            2,
            msg="Incorrect quantity of orders created",
        )
        self.assertEqual(
            models.OrderItem.objects.all().count(),
            3,
            msg="Incorrect quantity of order items created",
        )

    def test_update_purchase(self):
        """
        Ensure customers can update their order information
        """
        data = {
            "country": "Japan",
            "city": "Tokio",
            "address": "178935",
            "notes": "White house",
        }

        url = reverse("purchase-update", kwargs={"order_id": self.order.pk})
        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            models.Order.objects.filter(country="Japan", notes="White house").exists(),
            msg="The order information was not updated correctly",
        )

    def test_delete_purchase(self):
        """
        Ensure customer can cancel/delete their active orders
        """
        url = reverse("purchase-delete", kwargs={"order_id": self.order.pk})
        response = self.client.delete(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            models.Order.objects.filter(pk=self.order.pk).exists(),
            msg="The order was not deleted",
        )

    def test_list_history(self):
        """
        Ensure customers can list their purchase history
        """
        url = reverse("history-list")
        response = self.client.get(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [utils.compose_purchase(self.order_item)],
            msg="Incorrect format of purchases information",
        )

    def test_retrieve_history(self):
        """
        Ensure customers can retrieve a specific purchase information
        """
        url = reverse("history-retrieve", kwargs={"order_item_id": self.order_item.pk})
        response = self.client.get(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            utils.compose_purchase(self.order_item),
            msg="Incorrect format of purchase information",
        )
