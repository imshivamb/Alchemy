from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.views import APIView
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from ..models import SecurityLog
from ..models.user import User
from rest_framework import status
from django.conf import settings
from ..serializers.auth import SocialAuthResponseSerializer, UserSerializer
import logging
import requests

logger = logging.getLogger(__name__)

class BaseSocialLoginView(SocialLoginView):
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer
    response_serializer_class = SocialAuthResponseSerializer

    def get_client_info(self):
        return {
            'ip_address': self.request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() 
                         or self.request.META.get('REMOTE_ADDR'),
            'user_agent': self.request.META.get('HTTP_USER_AGENT', ''),
            'provider': self.adapter_class.__name__.replace('OAuth2Adapter', '').lower()
        }

    def get_response(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        response = super().get_response()
        
        if response.status_code == 200:
            user = self.user
            client_info = self.get_client_info()
            
            # Log the successful authentication
            SecurityLog.objects.create(
                user=user,
                action=f"{client_info['provider']}_auth_success",
                details={
                    'ip_address': client_info['ip_address'],
                    'user_agent': client_info['user_agent'],
                    'provider': client_info['provider']
                }
            )

            response_data = {
                'access': response.data.get('access_token'),
                'refresh': response.data.get('refresh_token'),
                'user': UserSerializer(user).data,
                'is_new_user': getattr(self, 'is_new_user', False),
                'social_provider': client_info['provider']
            }

            return Response(response_data)

        return response


class GoogleLoginView(APIView):
    def post(self, request):
        try:
            code = request.data.get('code')
            
            # Exchange code for tokens with Google
            token_response = requests.post('https://oauth2.googleapis.com/token', data={
                'code': code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_OAUTH_CALLBACK_URL,
                'grant_type': 'authorization_code'
            })
            
            token_data = token_response.json()
            
            if 'error' in token_data:
                return Response({'error': token_data['error']}, status=status.HTTP_400_BAD_REQUEST)
                
            # Get user info from Google
            user_info = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', 
                headers={'Authorization': f'Bearer {token_data["access_token"]}'}).json()
            
            # Get or create user (implement this based on your User model)
            user, created = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                }
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
            
        except Exception as e:
            logger.error(f"Google login error: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GitHubLoginView(BaseSocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.GITHUB_OAUTH_CALLBACK_URL

    def post(self, request, *args, **kwargs):
        try:
            code = request.data.get('code')
            logger.debug(f"Received GitHub auth code: {code[:10] if code else None}...")

            if not code:
                return Response(
                    {'error': 'Authorization code is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Exchange code for token
            token_url = "https://github.com/login/oauth/access_token"
            token_data = {
                'code': code,
                'client_id': settings.GITHUB_CLIENT_ID,
                'client_secret': settings.GITHUB_CLIENT_SECRET,
                'redirect_uri': self.callback_url
            }
            headers = {'Accept': 'application/json'}

            token_response = requests.post(token_url, data=token_data, headers=headers)
            token_json = token_response.json()

            if 'error' in token_json:
                logger.error(f"GitHub token exchange error: {token_json}")
                return Response(
                    {'error': token_json.get('error_description', token_json['error'])},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request.data['access_token'] = token_json['access_token']
            
            return super().post(request, *args, **kwargs)

        except Exception as e:
            logger.error(f"GitHub login error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )