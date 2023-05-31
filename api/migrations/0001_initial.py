# Generated by Django 4.2.1 on 2023-05-31 22:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=1000)),
                ('website_url', models.CharField(max_length=255)),
                ('logo_url', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=1000)),
                ('icon', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthdate', models.DateField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('0', 'Other')], default='0', max_length=10)),
                ('phone', models.CharField(max_length=45)),
                ('country', models.CharField(max_length=45)),
                ('city', models.CharField(max_length=45)),
                ('address', models.CharField(max_length=1000)),
                ('points', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000)])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryMan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthdate', models.DateField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('0', 'Other')], default='0', max_length=10)),
                ('phone', models.CharField(max_length=45)),
                ('country', models.CharField(max_length=45)),
                ('city', models.CharField(max_length=45)),
                ('address', models.CharField(max_length=1000)),
                ('vehicle_capacity', models.CharField(choices=[('SM', 'Small'), ('MD', 'Medium'), ('LG', 'Large')], max_length=10)),
                ('license_plate_number', models.CharField(max_length=255)),
                ('availability', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1000)),
                ('color', models.CharField(max_length=45)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('offer_price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('installments', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(24)])),
                ('stock', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(10000)])),
                ('months_warranty', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(36)])),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.brand')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.category')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('quantity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('shipping_charge', models.DecimalField(decimal_places=2, editable=False, max_digits=4)),
                ('delivered', models.BooleanField()),
                ('purchase_date', models.DateField(auto_now_add=True)),
                ('delivery_term', models.DateField()),
                ('notes', models.CharField(default='', max_length=255, validators=[django.core.validators.MinLengthValidator(0)])),
                ('payment_method', models.CharField(max_length=45)),
                ('country', models.CharField(max_length=45)),
                ('city', models.CharField(max_length=45)),
                ('address', models.CharField(max_length=1000)),
                ('postal_code', models.CharField(max_length=255)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.customer')),
                ('delivery_man', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.deliveryman')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.product')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('title', models.CharField(max_length=45)),
                ('content', models.CharField(default='', max_length=500, validators=[django.core.validators.MinLengthValidator(0)])),
                ('date', models.DateField(auto_now_add=True)),
                ('likes', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(10000)])),
                ('dislikes', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(10000)])),
                ('useful', models.BooleanField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
            options={
                'unique_together': {('customer', 'product')},
            },
        ),
        migrations.CreateModel(
            name='ProductSpecification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=45)),
                ('value', models.CharField(max_length=45)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
            options={
                'unique_together': {('key', 'product')},
            },
        ),
    ]