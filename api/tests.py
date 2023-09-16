from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from django.urls import reverse
from django.contrib.auth.hashers import make_password

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
        self.assertEqual(response.data, [utils.compose_product(self.product)])

    def test_retrieve_products(self):
        """
        Ensure anyone can retrieve a specific product by its ID
        """
        url = reverse("product-retrieve", kwargs={"product_id": 2})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, utils.compose_product(self.product))


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

        self.access_token = AccessToken.for_user(self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Bearer {self.access_token}"}

    def test_create_customer(self):
        """
        Ensure anyone can create a new account
        """
        url = reverse("customer-create")
        response = self.client.post(
            url,
            data={
                "username": "newuser30yo",
                "email": "newuser@gmail.com",
                "password": "NUpass#3011",
                "birthdate": "2001-04-11",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        self.assertEqual(response.data, utils.compose_customer(self.customer))

    def test_update_customer(self):
        """
        Ensure customers can update their account information
        """
        url = reverse("customer-update")
        response = self.client.patch(
            url,
            data={
                "username": "godtiergo",
                "email": "ivan@gmail.com",
                "firstname": "Iván",
                "country": "Chile",
                "password": "ADaska#$99",
            },
            **self.headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_customer(self):
        """
        Ensure customers can delete their accounts
        """
        url = reverse("customer-delete")
        response = self.client.delete(
            url, data={"password": "ADaska#$99"}, **self.headers
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_customer_interactions(self):
        """
        Ensure customer can list their interactions which corresponds to
        likes, dislikes and reports made on reviews
        """
        url = reverse("customer-list")
        response = self.client.get(url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"likes": [], "dislikes": [], "reports": []})
