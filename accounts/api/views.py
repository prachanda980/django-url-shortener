from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from ..models import User
from .serializers import UserSerializer, RegisterSerializer
import logging

logger = logging.getLogger('accounts')

class UserDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve details of the authenticated user.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        logger.info(f"API User detail accessed: {self.request.user.email}")
        return self.request.user

class RegisterAPIView(generics.CreateAPIView):
    """
    API endpoint to register a new user.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class LoginAPIView(APIView):
    """
    API endpoint to obtain JWT tokens.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)