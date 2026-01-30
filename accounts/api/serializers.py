from rest_framework import serializers
from ..models import User
from shortener.api.serializers import ShortURLSerializer

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Includes a nested representation of the user's short URLs (read-only).
    """
    urls = ShortURLSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'urls']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'gender']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender', '')
        )
        return user