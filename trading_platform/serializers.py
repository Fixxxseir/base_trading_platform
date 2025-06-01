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
    supplier = serializers.SlugRelatedField(
        slug_field="name", queryset=NetworkNode.objects.all(), required=False
    )
    owner = serializers.StringRelatedField()

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
        read_only_fields = ("debt", "created_at", "level")

    def create(self, validated_data):
        contact_data = validated_data.pop("contact")
        products_data = validated_data.pop("products")

        contact = Contact.objects.create(**contact_data)
        node = NetworkNode.objects.create(contact=contact, **validated_data)

        for product_data in products_data:
            product, _ = Product.objects.get_or_create(**product_data)
            node.products.add(product)

        return node
