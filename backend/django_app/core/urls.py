# backend/django_app/core/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints (v1)
    path('api/v1/', include([
        # Authentication endpoints
        path('auth/', include('authentication.urls')),
        
        # Workflow endpoints
        path('', include('workflow_engine.urls')),
        
        # JWT Token endpoints (if you want them separate from auth)
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),
]