from django.core.exceptions import ValidationError
from django.db import models

from users.models import User


class Contact(models.Model):
    email = models.EmailField(
        max_length=254,
        verbose_name="Email",
        help_text="Email контакта",
    )
    country = models.CharField(
        max_length=100, verbose_name="Страна", help_text="Страна контакта"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
        help_text="Город контакта",
    )
    street = models.CharField(
        max_length=100,
        verbose_name="Улица",
        help_text="Улица контакта",
    )
    house_number = models.CharField(
        max_length=20,
        verbose_name="Номер дома",
        help_text="Номер дома контакта",
    )

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return (
            f"{self.country}, {self.city}, {self.street} {self.house_number}"
        )


class Product(models.Model):
    name = models.CharField(
        max_length=254,
        verbose_name="Название",
        help_text="Название продукта",
    )
    model = models.CharField(
        max_length=254,
        verbose_name="Модель",
        help_text="Модель продукта",
    )
    release_date = models.DateField(
        verbose_name="Дата выхода",
        help_text="Дата выхода продукта",
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.name} {self.model}"


class NetworkNode(models.Model):
    FACTORY = 0
    RETAIL = 1
    ENTREPRENEUR = 2

    LEVEL_CHOICES = (
        (FACTORY, "Завод"),
        (RETAIL, "Розничная сеть"),
        (ENTREPRENEUR, "Индивидуальный предприниматель"),
    )

    name = models.CharField(
        max_length=254,
        verbose_name="Название",
        help_text="Название сети",
    )
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        verbose_name="Уровень",
        help_text="Уровень в иерархии",
    )
    contact = models.OneToOneField(
        Contact,
        on_delete=models.CASCADE,
        related_name="node",
        verbose_name="Контакты сети",
        help_text="Контакты сети",
    )
    products = models.ManyToManyField(
        Product, verbose_name="Продукты сети", help_text="Продукты сети"
    )
    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Поставщик",
        help_text="Поставщик продукции",
    )
    debt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Задолженность",
        help_text="Задолженность перед поставщиком",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата созданя",
        help_text="Дата создания сети",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="network_nodes",
        verbose_name="Основатель",
        help_text="Основатель сети",
    )

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"

    def __str__(self):
        return f"{self.get_level_display()}: {self.name}"

    def clean(self):
        if self.supplier == self:
            raise ValidationError(
                "Узел сети не может быть поставщиком самого себя."
            )
        if not self.supplier:
            self.level = self.FACTORY
        elif self.supplier.level == self.FACTORY:
            self.level = self.RETAIL
        else:
            self.level = self.ENTREPRENEUR

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
