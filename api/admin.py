from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Category)
class Category(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
    )
    list_display_links = ("title",)


@admin.register(models.Brand)
class Brand(admin.ModelAdmin):
    list_display = ("id", "name", "website_url")
    list_display_links = ("name",)


@admin.register(models.Customer)
class Customer(admin.ModelAdmin):
    list_display = ("id", "get_username", "get_email")
    list_display_links = ("get_username",)

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    get_username.short_description = "Username"
    get_email.short_description = "Email"


@admin.register(models.DeliveryMan)
class DeliveryMan(admin.ModelAdmin):
    list_display = ("id", "get_username", "get_email")
    list_display_links = ("get_username",)

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    get_username.short_description = "Username"
    get_email.short_description = "Email"


@admin.register(models.Product)
class Product(admin.ModelAdmin):
    list_display = ("id", "name", "price", "brand", "category", "is_gamer")
    list_display_links = ("name",)


@admin.register(models.ProductSpecification)
class ProductSpecification(admin.ModelAdmin):
    list_display = ("id", "key", "value", "product")
    list_display_links = ("key",)


@admin.register(models.ProductImage)
class ProductImage(admin.ModelAdmin):
    list_display = ("id", "product", "description", "is_default")
    list_display_links = ("product",)


@admin.register(models.Review)
class Review(admin.ModelAdmin):
    list_display = ("id", "product", "customer", "rating")
    list_display_links = ("product",)


@admin.register(models.Order)
class Order(admin.ModelAdmin):
    list_display = (
        "id",
        "paid",
        "dispatched",
        "on_the_way",
        "delivered",
        "delivery_man",
    )
    list_display_links = ("paid",)


@admin.register(models.OrderItem)
class OrderItem(admin.ModelAdmin):
    list_display = ("id", "product", "customer")
    list_display_links = ("product",)


@admin.register(models.CartItem)
class CardItem(admin.ModelAdmin):
    list_display = ("id", "product", "customer")
    list_display_links = ("product",)


@admin.register(models.FavItem)
class FavItem(admin.ModelAdmin):
    list_display = ("id", "product", "customer")
    list_display_links = ("product",)


@admin.register(models.Coupon)
class Coupon(admin.ModelAdmin):
    list_display = ("id", "title", "amount", "customer")
    list_display_links = ("title",)
