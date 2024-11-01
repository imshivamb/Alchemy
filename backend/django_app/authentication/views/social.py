from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from ..models import SecurityLog

class BaseSocialLoginView(SocialLoginView):
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        if response.status_code == 200:
            user = self.user
            
            # Log social login
            SecurityLog.objects.create(
                user=user,
                action=f"{self.adapter_class.__name__.lower()}_login",
                details={
                    'provider': self.adapter_class.__name__.replace('OAuth2Adapter', '')
                }
            )
            
            response.data.update({
                'user_id': str(user.id),
                'email': user.email,
                'plan_type': user.profile.plan_type,
                'is_staff': user.is_staff,
                'is_verified': user.is_verified,
                'profile_picture': user.profile_picture.url if user.profile_picture else None
            })
        return response

class GoogleLoginView(BaseSocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client

    def get_response(self):
        try:
            return super().get_response()
        except Exception as e:
            return Response(
                {'error': 'Failed to authenticate with Google'},
                status=status.HTTP_400_BAD_REQUEST
            )

class GitHubLoginView(BaseSocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.GITHUB_OAUTH_CALLBACK_URL
    client_class = OAuth2Client

    def get_response(self):
        try:
            return super().get_response()
        except Exception as e:
            return Response(
                {'error': 'Failed to authenticate with GitHub'},
                status=status.HTTP_400_BAD_REQUEST
            )