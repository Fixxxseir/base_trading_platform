from loguru import logger
from rest_framework import serializers
from .models import Contact, Product, NetworkNode
from django.contrib.auth.models import User


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class NetworkNodeSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    products = ProductSerializer(many=True)
    supplier = serializers.HyperlinkedRelatedField(
        view_name="trading_platform:network-node-detail",
        read_only=True,
        required=False,
    )
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            "id",
            "name",
            "level",
            "contact",
            "products",
            "supplier",
            "debt",
            "created_at",
            "owner",
        ]
        read_only_fields = (
            "debt",
            "created_at",
            "level",
            "owner",
        )

    def create(self, validated_data):
        logger.info(f"Создание NetworkNode с данными: {validated_data}")
        contact_data = validated_data.pop("contact")
        products_data = validated_data.pop("products")

        contact = Contact.objects.create(**contact_data)
        node = NetworkNode.objects.create(contact=contact, **validated_data)

        for product_data in products_data:
            product, created = Product.objects.get_or_create(**product_data)
            if created:
                logger.info(f"Создан новый продукт: {product.name}")
            node.products.add(product)

        logger.info(f"NetworkNode создан с id={node.id}")
        return node

    def update(self, instance, validated_data):
        if "debt" in self.initial_data:
            logger.warning(
                f"Попытка обновления поля 'debt' у NetworkNode id={instance.id} запрещена"
            )
            raise serializers.ValidationError(
                {"debt": "Обновление задолженности запрещено."}
            )
        logger.info(
            f"Обновление NetworkNode id={instance.id} с данными: {validated_data}"
        )
        return super().update(instance, validated_data)
