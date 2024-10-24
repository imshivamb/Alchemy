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
    GoogleLoginView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('email/verify/', EmailVerificationView.as_view(), name='email-verify'),
    path('limits/', UserLimitsView.as_view(), name='user-limits'),
    path('google/', GoogleLoginView.as_view(), name='google_login'),
]