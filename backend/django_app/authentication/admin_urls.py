from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminUserViewSet,
    AdminTeamViewSet,
)

# Create router for admin viewsets
router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'teams', AdminTeamViewSet, basename='admin-team')

urlpatterns = [
    path('', include(router.urls)),
]