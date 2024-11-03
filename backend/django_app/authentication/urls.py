# authentication/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserViewSet,
    TeamViewSet,
    APIKeyViewSet,
    PasswordResetView,
    EmailVerificationView,
    UserLimitsView,
    GoogleLoginView,
    GitHubLoginView,
    AdminUserViewSet,
    AdminTeamViewSet,
    PasswordResetConfirmView,
    UserMeView
)

# API Routers
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')

# Admin routes
admin_router = DefaultRouter()
admin_router.register(r'users', AdminUserViewSet, basename='admin-user')
admin_router.register(r'teams', AdminTeamViewSet, basename='admin-team')

urlpatterns = [
    # Base router URLs (for ViewSets)
    path('', include(router.urls)),
    
    # Auth endpoints
    path('login/', LoginView.as_view(), name='auth_login'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    
    # Token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Password management
    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('email/verify/', EmailVerificationView.as_view(), name='email_verify'),
    
    # User specific endpoints
    path('me/', UserMeView.as_view(), name='user_me'),
    path('limits/', UserLimitsView.as_view(), name='user_limits'),
    
    # Social auth endpoints
    path('social/', include([
        path('google/', GoogleLoginView.as_view(), name='google_login'),
        path('github/', GitHubLoginView.as_view(), name='github_login'),
    ])),
    
    # Admin endpoints
    path('admin/', include(admin_router.urls)),
]

# The final URLs will be:
# api/v1/auth/login/
# api/v1/auth/register/
# api/v1/auth/logout/
# api/v1/auth/token/refresh/
# api/v1/auth/token/verify/
# api/v1/auth/password/reset/
# api/v1/auth/email/verify/
# api/v1/auth/me/
# api/v1/auth/limits/
# api/v1/auth/social/google/
# api/v1/auth/social/github/
# api/v1/auth/users/
# api/v1/auth/teams/
# api/v1/auth/api-keys/
# api/v1/auth/admin/users/
# api/v1/auth/admin/teams/