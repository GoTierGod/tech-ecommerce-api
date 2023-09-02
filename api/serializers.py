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
    user = UserSerializer()

    class Meta:
        model = models.Customer
        fields = "__all__"


class DeliveryManSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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
    product = serializers.StringRelatedField()

    class Meta:
        model = models.ProductSpecification
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = models.ProductImage
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    product = serializers.StringRelatedField()

    class Meta:
        model = models.Review
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    delivery_man = serializers.StringRelatedField()

    class Meta:
        model = models.Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()
    product = serializers.StringRelatedField()
    order = serializers.StringRelatedField()

    class Meta:
        model = models.OrderItem
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    customer = serializers.StringRelatedField()

    class Meta:
        model = models.CartItem
        fields = "__all__"


class FavItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    customer = serializers.StringRelatedField()

    class Meta:
        model = models.FavItem
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = models.Coupon
        fields = "__all__"
