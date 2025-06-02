from loguru import logger
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import NetworkNode
from .permissions import IsActiveUser
from .serializers import NetworkNodeSerializer


class NetworkNodeViewSet(viewsets.ModelViewSet):
    queryset = (
        NetworkNode.objects.select_related("contact", "supplier", "owner")
        .prefetch_related("products")
        .order_by("id")
    )
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "contact__country": ["exact"],
        "level": ["exact"],
        "created_at": ["gte", "lte"],
    }

    def perform_create(self, serializer):
        logger.info(f"Создание сети пользователем: {self.request.user}")
        serializer.save(owner=self.request.user)
