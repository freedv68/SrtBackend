from django.urls import include, re_path, path
from rest_framework.routers import DefaultRouter

from bags.views import BagDateViewSet, BagPortViewSet, BagNumberViewSet, BagHawbNoViewSet

router = DefaultRouter()
router.register(r'bagDate', BagDateViewSet)
router.register(r'bagPort', BagPortViewSet)
router.register(r'bagNumber', BagNumberViewSet)
router.register(r'bagHawbNo', BagHawbNoViewSet)

urlpatterns = [
    re_path(r'^', include(router.urls)),
]
