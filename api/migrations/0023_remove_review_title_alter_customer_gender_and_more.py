# Generated by Django 4.2.1 on 2023-09-11 10:52

import api.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_review_hidden'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='title',
        ),
        migrations.AlterField(
            model_name='customer',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='deliveryman',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='content',
            field=models.CharField(default='', validators=[django.core.validators.MinLengthValidator(10), django.core.validators.MaxValueValidator(45), api.validators.profanity_filter]),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
