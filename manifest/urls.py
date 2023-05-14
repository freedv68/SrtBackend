from django.urls import include, re_path, path
from rest_framework.routers import DefaultRouter

from manifest.views import ManifestViewSet, ManifestHawbNoViewSet, ManifestPortViewSet, ManifestTeamViewSet, ManifestInsertDateViewSet, ManifestAssignmentTeamsViewSet


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'manifest', ManifestViewSet)
router.register(r'manifestHawbNo', ManifestHawbNoViewSet)
router.register(r'manifestPort', ManifestPortViewSet)
router.register(r'manifestTeam', ManifestTeamViewSet)
router.register(r'manifestInsertDate', ManifestInsertDateViewSet)
router.register(r'manifestAssignmentTeams', ManifestAssignmentTeamsViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    re_path(r'^', include(router.urls)),
    # re_path(r'^manifest/bulk_create/', ManifestViewSet.as_view({'bulk_create'}), name='bulk_create')
    # re_path(r'manifest/', ManifestViewSet.as_view({'update'})),
    # path('manifest/<str:pk>/', ManifestViewSet.as_view({'get': 'update'})),
]
