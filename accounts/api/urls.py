from django.urls import path
from .views import RegisterAPIView, LoginAPIView, UserDetailAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('me/', UserDetailAPIView.as_view(), name='api_user_detail'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
]