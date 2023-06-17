from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from bags.views import BagDateViewSet, BagPortViewSet, BagPortListViewSet, BagNumberViewSet, BagHawbNoViewSet, BagCheckHawbNoViewSet, BagHawbNoListViewSet

router = DefaultRouter()
router.register(r'bagDate', BagDateViewSet)
router.register(r'bagPort', BagPortViewSet)
router.register(r'bagPortList', BagPortListViewSet)
router.register(r'bagNumber', BagNumberViewSet)
router.register(r'bagHawbNo', BagHawbNoViewSet)
router.register(r'bagCheckHawbNo', BagCheckHawbNoViewSet)
router.register(r'bagHawbNoList', BagHawbNoListViewSet)

urlpatterns = [
    re_path(r'^', include(router.urls)),
]
