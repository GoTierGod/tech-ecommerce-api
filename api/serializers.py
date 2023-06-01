from django.contrib.auth.models import User
from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Brand
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = "__all__"


class DeliveryManSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryMan
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    category = CategorySerializer()

    class Meta:
        model = models.Product
        fields = "__all__"


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductSpecification
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()
    product = serializers.StringRelatedField()

    class Meta:
        model = models.Review
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()
    product = serializers.StringRelatedField()
    delivery_man = serializers.StringRelatedField()

    class Meta:
        model = models.Order
        fields = "__all__"
