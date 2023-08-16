# Generated by Django 4.2.1 on 2023-08-16 23:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_rename_useful_review_is_useful'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='dislikes',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='is_useful',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='review',
            name='likes',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10000)]),
        ),
    ]
