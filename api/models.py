from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
)
from django.core.exceptions import ValidationError


# Models
class Category(models.Model):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=1000)
    icon = models.CharField(max_length=45)

    def __str__(self) -> str:
        return self.title


class Brand(models.Model):
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=1000)
    website_url = models.CharField(max_length=255)
    logo_url = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Customer(models.Model):
    birthdate = models.DateField()
    GENDERS = (("M", "Male"), ("F", "Female"), ("0", "Other"))
    gender = models.CharField(
        max_length=10,
        choices=GENDERS,
        default=GENDERS[2][0],
    )
    phone = models.CharField(max_length=45)
    country = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    address = models.CharField(max_length=1000)
    points = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(1000000)]
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.user.first_name} {self.user.last_name})"


class DeliveryMan(models.Model):
    birthdate = models.DateField()
    GENDERS = (("M", "Male"), ("F", "Female"), ("0", "Other"))
    gender = models.CharField(max_length=10, choices=GENDERS, default=GENDERS[2][0])
    phone = models.CharField(max_length=45)
    country = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    address = models.CharField(max_length=1000)
    CAPACITIES = (("SM", "Small"), ("MD", "Medium"), ("LG", "Large"))
    vehicle_capacity = models.CharField(max_length=10, choices=CAPACITIES)
    license_plate_number = models.CharField(max_length=255)
    availability = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.user.first_name} {self.user.last_name})"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=4000)
    color = models.CharField(max_length=45)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    offer_price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    installments = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)])
    stock = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10000)])
    months_warranty = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(36)]
    )
    is_gamer = models.BooleanField(default=False)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.name


class ProductSpecification(models.Model):
    key = models.CharField(max_length=45)
    value = models.CharField(max_length=45)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.key} : {self.value}"

    class Meta:
        unique_together = ("key", "product")


class ProductImage(models.Model):
    url = models.CharField(max_length=255)
    description = models.CharField(max_length=45)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.description

    def save(self, *args, **kwargs):
        if self.is_default:
            if ProductImage.objects.filter(
                product=self.product, is_default=True
            ).exists():
                ProductImage.objects.filter(
                    product=self.product, is_default=True
                ).update(is_default=False)

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("url", "product")


class Review(models.Model):
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    title = models.CharField(max_length=45)
    content = models.CharField(
        max_length=500, default="", validators=[MinLengthValidator(0)]
    )
    date = models.DateField(auto_now_add=True, editable=False)
    is_useful = models.BooleanField(default=False)
    hidden = models.BooleanField(default=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.customer.user.first_name} - {self.product.name}"

    def clean(self) -> None:
        super().clean()
        if self.rating % 0.5 != 0:
            raise ValidationError("Rating can only be incremented by 0.5.")

    class Meta:
        unique_together = ("customer", "product")


class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("review", "customer")


class ReviewDislike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("review", "customer")


class ReviewReport(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("review", "customer")


class Order(models.Model):
    paid = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    purchase_date = models.DateField(auto_now_add=True, editable=False)
    delivery_term = models.DateField()
    dispatched = models.BooleanField(default=False)
    on_the_way = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=45)
    country = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    address = models.CharField(max_length=1000)
    notes = models.CharField(max_length=255, default="")
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, default=None, null=True
    )
    delivery_man = models.ForeignKey(
        DeliveryMan, on_delete=models.SET_NULL, default=None, null=True
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.paid} - {self.dispatched} - {self.on_the_way} - {self.delivered} - {self.delivery_man}"

    def clean(self) -> None:
        super().clean()
        max_active_orders = 3
        current_active_orders = Order.objects.filter(
            customer=self.customer, delivered=False
        ).count()

        if current_active_orders >= max_active_orders:
            raise ValidationError("You cannot have more than 3 active orders.")


class OrderItem(models.Model):
    total_cost = models.DecimalField(max_digits=7, decimal_places=2, editable=False)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.customer.user.username}"

    def save(self, *args, **kwargs):
        self.total_cost = self.product.offer_price * self.quantity

        super().save(*args, **kwargs)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.customer.user.username} - {self.product.name}"

    def clean(self) -> None:
        super().clean()
        max_cart_items = 10
        current_cart_items = CartItem.objects.filter(customer=self.customer).count()

        if current_cart_items >= max_cart_items:
            raise ValidationError("You cannot add more than 10 products to your cart.")

    class Meta:
        unique_together = ("product", "customer")


class FavItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.customer.user.username} - {self.product.name}"

    def clean(self) -> None:
        super().clean()
        max_favorite_items = 25
        current_favorite_items = FavItem.objects.filter(customer=self.customer).count()

        if current_favorite_items >= max_favorite_items:
            raise ValidationError(
                "You cannot add more than 25 products to your favorites."
            )

    class Meta:
        unique_together = ("product", "customer")


class Coupon(models.Model):
    title = models.CharField(max_length=45)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.amount} {self.customer.user.username}"
