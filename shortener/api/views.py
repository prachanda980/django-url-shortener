from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from ..models import ShortURL
from .serializers import ShortURLSerializer
import logging

logger = logging.getLogger('shortener')

class ShortURLListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list and create short URLs.

    GET: Returns a list of all short URLs for the authenticated user.
    POST: Creates a new short URL.
    """
    serializer_class = ShortURLSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShortURL.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        url = serializer.save(user=self.request.user)
        logger.info(f"API ShortURL created by {self.request.user.email}: {url.short_key or url.custom_key}")

class ShortURLRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific short URL.

    Supports lookup by both 'short_key' and 'custom_key'.
    """
    serializer_class = ShortURLSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'short_key'

    def get_queryset(self):
        return ShortURL.objects.filter(user=self.request.user)
    
    def get_object(self):
        """
        Retrieve the ShortURL instance.

        Tries to look up by short_key first, then falls back to custom_key.
        """
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        
        # Also try custom_key if short_key fails
        obj = queryset.filter(models.Q(short_key=self.kwargs[lookup_url_kwarg]) | models.Q(custom_key=self.kwargs[lookup_url_kwarg])).first()
        if not obj:
            from django.http import Http404
            logger.warning(f"API 404 for ShortURL: {self.kwargs[lookup_url_kwarg]}")
            raise Http404
        
        if self.request.method == 'DELETE':
             logger.info(f"API ShortURL deleted by {self.request.user.email}: {obj.short_key or obj.custom_key}")
        
        return obj
