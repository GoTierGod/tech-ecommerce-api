from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Category)
class Category(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(models.Brand)
class Brand(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(models.Customer)
class Customer(admin.ModelAdmin):
    list_display = ("id", "user")


@admin.register(models.DeliveryMan)
class DeliveryMan(admin.ModelAdmin):
    list_display = ("id", "user")


@admin.register(models.Product)
class Product(admin.ModelAdmin):
    list_display = ("id", "name", "price")


@admin.register(models.ProductSpecification)
class ProductSpecification(admin.ModelAdmin):
    list_display = ("id", "key", "value", "product")


@admin.register(models.Review)
class Review(admin.ModelAdmin):
    list_display = ("id", "product", "customer", "rating")


@admin.register(models.Order)
class Order(admin.ModelAdmin):
    list_display = ("id", "product", "country", "city")
