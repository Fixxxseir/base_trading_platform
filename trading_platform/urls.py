from rest_framework.routers import DefaultRouter

from .apps import TradingPlatformConfig
from .views import NetworkNodeViewSet

app_name = TradingPlatformConfig.name

router = DefaultRouter()
router.register(r"nodes", NetworkNodeViewSet, basename="network-node")

urlpatterns = router.urls
