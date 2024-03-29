# Generated by Django 4.2.1 on 2023-08-15 01:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_rename_carditem_cartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_cost',
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_man',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='api.deliveryman'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_cost', models.DecimalField(decimal_places=2, editable=False, max_digits=7)),
                ('quantity', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.customer')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.product')),
            ],
        ),
    ]
