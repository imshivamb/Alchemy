from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowViewSet,
    WorkflowTaskViewSet,
    WebhookViewSet,
    WebhookLogViewSet
)

# Creating a router and registering viewsets with it

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'tasks', WorkflowTaskViewSet, basename='task')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'webhook-logs', WebhookLogViewSet, basename='webhook-log')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]