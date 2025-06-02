from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.template.context_processors import request
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Contact, Product, NetworkNode

User = get_user_model()


class NetworkNodeTestCase(APITestCase):
    """
    Тесты создание продуктов, контактов сетей и сетей
    """

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            email="test1@test.ru",
            username="test1",
            password="test1",
            is_active=True,
        )
        self.user2 = User.objects.create_user(
            email="test2@test.ru",
            username="test2",
            password="test2",
            is_active=True,
        )
        self.user3 = User.objects.create_user(
            email="test3@test.ru",
            username="test3",
            password="test3",
            is_active=True,
        )
        self.user4 = User.objects.create_user(
            email="test4@test.ru",
            username="test4",
            password="test4",
            is_active=False,
        )
        self.product1 = Product.objects.create(
            name="product1",
            model="product1",
            release_date="2021-01-01",
        )
        self.product2 = Product.objects.create(
            name="product2",
            model="product2",
            release_date="2022-02-02",
        )
        self.product3 = Product.objects.create(
            name="product3",
            model="product3",
            release_date="2023-03-03",
        )
        self.contact1 = Contact.objects.create(
            email="contact1@test.ru",
            country="contact1",
            city="contact1",
            street="contact1",
            house_number="1",
        )
        self.contact2 = Contact.objects.create(
            email="contact2@test.ru",
            country="contact2",
            city="contact2",
            street="contact2",
            house_number="2",
        )
        self.contact3 = Contact.objects.create(
            email="contact3@test.ru",
            country="contact3",
            city="contact3",
            street="contact3",
            house_number="3",
        )
        self.factory1 = NetworkNode.objects.create(
            name="Предприятие1",
            contact=self.contact1,
            owner=self.user1,
        )
        self.factory1.products.set([self.product1])

        self.factory2 = NetworkNode.objects.create(
            name="Предприятие2",
            contact=self.contact2,
            owner=self.user2,
        )
        self.factory2.products.set([self.product2])

        self.retail = NetworkNode.objects.create(
            name="Retail Network",
            contact=self.contact3,
            supplier=self.factory1,
            owner=self.user3,
        )
        self.retail.products.set([self.product3])

    def test_network_node_creation(self):
        """Тест создания узлов сети"""
        self.assertEqual(NetworkNode.objects.count(), 3)
        self.assertEqual(self.factory1.level, NetworkNode.FACTORY)
        self.assertEqual(self.retail.level, NetworkNode.RETAIL)
        self.assertEqual(self.factory1.products.count(), 1)
        self.assertEqual(self.retail.products.first(), self.product3)

    def test_network_node_str(self):
        """Тест строкового представления узла сети"""
        self.assertEqual(str(self.factory1), "Завод: Предприятие1")
        self.assertEqual(str(self.retail), "Розничная сеть: Retail Network")

    def test_self_supplier_validation(self):
        """Тест валидации при попытке сделать узел поставщиком самого себя"""
        with self.assertRaises(ValidationError):
            self.factory1.supplier = self.factory1
            print(ValidationError)
            self.factory1.full_clean()

    def test_network_node_list_unauthorized(self):
        """Тест доступа к списку узлов без авторизации"""
        response = self.client.get(
            reverse("trading_platform:network-node-list")
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_network_node_list_authorized(self):
        """Тест доступа к списку узлов с авторизацией"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            reverse("trading_platform:network-node-list")
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"][0]["name"], "Предприятие1")

    def test_create_network_node(self):
        """Тест создания нового узла сети через API"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "name": "Розничная сеть",
            "contact": {
                "email": "v_roznicu@test.ru",
                "country": "Страна",
                "city": "Город",
                "street": "Улица",
                "house_number": "8",
            },
            "products": [
                {
                    "name": "продукт в розницу",
                    "model": "модель розничного продукта",
                    "release_date": "2024-04-04",
                }
            ],
            "supplier": self.factory1.name,
        }

        response = self.client.post(
            reverse("trading_platform:network-node-list"),
            data=data,
            format="json",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkNode.objects.count(), 4)
        self.assertEqual(response.data["name"], "Розничная сеть")
        self.assertEqual(response.data["level"], NetworkNode.RETAIL)

    def test_filter_network_nodes_by_country(self):
        """Тест фильтрации узлов по стране"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            reverse("trading_platform:network-node-list")
            + "?contact__country=contact2"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Предприятие2")

    def test_update_debt_not_allowed(self):
        """Тест запрета на обновление задолженности"""
        self.client.force_authenticate(user=self.user1)

        data = {"debt": "1000.00"}

        response = self.client.patch(
            reverse(
                "trading_platform:network-node-detail", args=[self.retail.id]
            ),
            data=data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("debt", response.data)
        self.assertEqual(
            str(response.data["debt"]), "Обновление задолженности запрещено."
        )

    def test_create_entrepreneur(self):
        """Тест создания индивидуального предпринимателя"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "name": "Индивидуальный предприниматель",
            "contact": {
                "email": "predprinimatel@test.ru",
                "country": "Страна",
                "city": "Город",
                "street": "Улица",
                "house_number": "8",
            },
            "products": [
                {
                    "name": "продукт предпринимателя",
                    "model": "модель предпринимателя",
                    "release_date": "2025-05-05",
                }
            ],
            "supplier": self.retail.name,
        }

        response = self.client.post(
            reverse("trading_platform:network-node-list"),
            data=data,
            format="json",
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["level"], NetworkNode.ENTREPRENEUR)
