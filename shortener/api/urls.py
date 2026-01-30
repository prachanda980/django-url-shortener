from django.urls import path
from .views import (
    ShortURLListCreateAPIView,
    ShortURLRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('shorten/', ShortURLListCreateAPIView.as_view(), name='api_url_list_create'),
    path('urls/<str:short_key>/', ShortURLRetrieveUpdateDestroyAPIView.as_view(), name='api_url_detail'),
]
