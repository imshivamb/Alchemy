from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common functionality"""
    permission_classes = [IsAuthenticated]
    schema = None

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        """Base queryset filtering by active status"""
        queryset = super().get_queryset()
        return queryset.filter(is_active=True)
    
    class Meta:
        abstract = True