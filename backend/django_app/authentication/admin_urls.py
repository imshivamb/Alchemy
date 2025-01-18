from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminUserViewSet,
    AdminTeamViewSet,
    AdminWorkspaceViewSet,
    AdminAnalyticsViewSet,
    AdminSystemViewSet,
    AdminActivityViewSet
)

# Create router for admin viewsets
router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-user')
router.register(r'teams', AdminTeamViewSet, basename='admin-team')
router.register(r'workspaces', AdminWorkspaceViewSet, basename='admin-workspace')
router.register(r'analytics', AdminAnalyticsViewSet, basename='admin-analytics')
router.register(r'system', AdminSystemViewSet, basename='admin-system')
router.register(r'activity', AdminActivityViewSet, basename='admin-activity')

urlpatterns = [
    path('', include(router.urls)),
]