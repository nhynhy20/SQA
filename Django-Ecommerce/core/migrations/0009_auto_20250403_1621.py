# Generated by Django 2.2.4 on 2025-04-03 09:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20250403_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True, validators=[django.core.validators.RegexValidator(message='Slug chỉ được chứa chữ cái thường, số, gạch ngang và dấu gạch dưới.', regex='^[a-z0-9\\-_]+$')]),
        ),
    ]
