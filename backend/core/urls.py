from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/v1/', include('workflow_engine.urls')), # workflow API endpoints
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('workflow_engine.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Add this line
]