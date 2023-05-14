from django.urls import path

"""
from rest_framework_simplejwt.views import (
    #TokenObtainPairView,
    #TokenRefreshView,
)
"""

from accounts.views import CustomTokenObtainPairView, LogoutView, CustomTokenRefreshView

#router.register(r'users', views.UserViewSet)

urlpatterns = [
    #path('', views.UserView.as_view()),
    #path('login/', views.UserView.as_view()),
    #path('logout/', views.UserView.as_view()),
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='custom_token_refresh'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
]
