# core/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

# Schema view configuration
schema_view = get_schema_view(
    openapi.Info(
        title="AI Automation Platform API",
        default_version='v1',
        description="""
        API Documentation for AI Automation Platform
        
        ## Available Endpoints:
        * /api/v1/auth/ - Authentication endpoints
        * /api/v1/admin/ - Admin operations
        * /api/v1/ - Workflow operations
        """,
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    urlconf='core.urls',  # This is important!
)

# API URL Patterns
api_v1_patterns = [
    # Authentication URLs
    path('auth/', include('authentication.urls')),
    # Admin URLs
    path('admin/', include('authentication.admin_urls')),
    # Workflow URLs
    path('', include('workflow_engine.urls')),
]

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API (v1)
    path('api/v1/', include(api_v1_patterns)),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]