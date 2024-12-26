from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from ..serializers.auth import SocialAuthResponseSerializer, UserSerializer
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from ..models import SecurityLog
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class BaseSocialLoginView(SocialLoginView):
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer
    response_serializer_class = SocialAuthResponseSerializer

    def get_provider_name(self):
        return self.adapter_class.__name__.replace('OAuth2Adapter', '').lower()

    def get_client_info(self):
        return {
            'ip_address': self.request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() 
                         or self.request.META.get('REMOTE_ADDR'),
            'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
            'provider': self.get_provider_name()
        }

    def get_response(self):
        response = super().get_response()
        logger.debug(f"Raw social auth response: {response.data}")
        
        if response.status_code == 200:
            user = self.user
            client_info = self.get_client_info()
            
            # Log the authentication
            SecurityLog.objects.create(
                user=user,
                action=f"{client_info['provider']}_auth_success",
                details={
                    'ip_address': client_info['ip_address'],
                    'user_agent': client_info['user_agent'],
                    'provider': client_info['provider']
                }
            )

            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            # Enhanced response data
            response_data = {
                'access': response.data.get('access_token'),
                'refresh': response.data.get('refresh_token'),
                'user': UserSerializer(user).data,
                'is_new_user': getattr(self, 'is_new_user', False),
                'social_provider': self.get_provider_name()
            }

            serializer = self.response_serializer_class(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        return response

    def handle_failed_auth(self, error):
        """Handle failed authentication"""
        client_info = self.get_client_info()
        
        SecurityLog.objects.create(
            action=f"{client_info['provider']}_auth_failed",
            details={
                'error': str(error),
                'ip_address': client_info['ip_address'],
                'user_agent': client_info['user_agent'],
                'provider': client_info['provider']
            }
        )
        
        return Response(
            {'error': f'Authentication failed: {str(error)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

class GoogleLoginView(BaseSocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL

    @swagger_auto_schema(
        operation_description="Authenticate with Google",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['access_token'],
            properties={
                'access_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Google OAuth2 access token'
                ),
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Google OAuth2 authorization code (optional)'
                )
            }
        ),
        responses={
            200: SocialAuthResponseSerializer,
            400: 'Authentication failed'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return self.handle_failed_auth(e)

class GitHubLoginView(BaseSocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.GITHUB_OAUTH_CALLBACK_URL

    @swagger_auto_schema(
        operation_description="Authenticate with GitHub",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['access_token'],
            properties={
                'access_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='GitHub OAuth access token'
                ),
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='GitHub OAuth authorization code (optional)'
                )
            }
        ),
        responses={
            200: SocialAuthResponseSerializer,
            400: 'Authentication failed'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return self.handle_failed_auth(e)
