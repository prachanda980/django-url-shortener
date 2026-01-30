from rest_framework import serializers
from ..models import ShortURL

class ShortURLSerializer(serializers.ModelSerializer):
    """
    Serializer for the ShortURL model.
    
    Handles the validation and transformations of ShortURL data for the API.
    """
    class Meta:
        model = ShortURL
        fields = ['id', 'original_url', 'short_key', 'custom_key', 'status', 'click_count', 'created_at', 'expiration_date', 'qr_code']
