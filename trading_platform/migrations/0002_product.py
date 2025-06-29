# Generated by Django 5.2.1 on 2025-06-01 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trading_platform", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Название продукта",
                        max_length=254,
                        verbose_name="Название",
                    ),
                ),
                (
                    "model",
                    models.CharField(
                        help_text="Модель продукта",
                        max_length=254,
                        verbose_name="Модель",
                    ),
                ),
                (
                    "release_date",
                    models.DateField(
                        help_text="Дата выхода продукта",
                        verbose_name="Дата выхода",
                    ),
                ),
            ],
            options={
                "verbose_name": "Продукт",
                "verbose_name_plural": "Продукты",
            },
        ),
    ]
