from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership, APIKey, UserProfile, LoginHistory
from workflow_engine.models import Workflow
from .serializers import (
    UserSerializer, 
    TeamSerializer, 
    TeamMembershipSerializer,
    EmailVerificationSerializer,
    PasswordResetSerializer,
    APIKeySerializer,
    UserProfileSerializer
)
import uuid

User = get_user_model()
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    throttle_classes = [AnonRateThrottle]

    
class LoginView(TokenObtainPairView):
    """
    Login view that extends TokenObtainPairView to add custom functionality
    like login history tracking
    """
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                user = User.objects.get(username=request.data.get('username'))
                
                # Create login history entry
                LoginHistory.objects.create(
                    user=user,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    location=self.get_location_from_ip(self.get_client_ip(request)),
                    status='success'
                )
                
                response.data.update({
                    'user_id': str(user.id),
                    'email': user.email,
                    'plan_type': user.profile.plan_type,
                    'is_staff': user.is_staff,
                })
                
            return response
        except Exception as e:
            LoginHistory.objects.create(
                user=User.objects.get(username=request.data.get('username')),
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status='failed',
                error_message=str(e)
            )
            raise

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def get_location_from_ip(self, ip):
        return 'Unknown'
    
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=True, methods=['post'])
    def generate_api_key(self, request, pk=None):
        user = self.get_object()
        api_key = APIKey.objects.create(user=user,
            name=f"API Key - {uuid.uuid4().hex[:8]}",
            key=uuid.uuid4().hex)
        return Response({
            'key': api_key.key,
            'name': api_key.name
        })
    
class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        TeamMembership.objects.create(user=self.request.user, team=team, role='admin')
        
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'viewer')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=user_id)
            TeamMembership.objects.create(user=user, team=team, role=role)
            return Response({'status': 'member added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            key=uuid.uuid4().hex
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
class EmailVerificationView(APIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        try:
            user = User.objects.get(email_verification_token=token)
            user.is_verified = True
            user.email_verification_token = None
            user.save()
            return Response({'detail': 'Email verified successfully'})
        except User.DoesNotExist:
            raise ValidationError('Invalid token')

class PasswordResetView(APIView):
    throttle_classes = [AnonRateThrottle]
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny] 

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'
                
                send_mail(
                    'Password Reset',
                    f'Click here to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except User.DoesNotExist:
                pass  # Don't reveal whether email exists
            
            return Response({'detail': 'Password reset email sent if account exists'})
        except Exception as e:
            return Response(
                {'error': 'Failed to process password reset request'},
                status=status.HTTP_400_BAD_REQUEST
            )

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/google/callback"  # frontend callback URL
    client_class = OAuth2Client
    
    def get_response(self):
        response = super().get_response()
        if response.status_code == 200:
            user = self.user
            response.data.update({
                'user_id': str(user.id),
                'email': user.email,
                'plan_type': user.profile.plan_type,
                'is_staff': user.is_staff,
            })
        return response
    
class GitHubLoginView(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = "http://localhost:3000/auth/github/callback"
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        if response.status_code == 200:
            user = self.user
            response.data.update({
                'user_id': str(user.id),
                'email': user.email,
                'plan_type': user.profile.plan_type,
                'is_staff': user.is_staff,
            })
        return response
    
class UserLimitsView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        try:
            user = request.user
            profile = user.profile

            workflow_limit = settings.WORKFLOW_LIMITS.get(
                profile.plan_type, 
                settings.DEFAULT_WORKFLOW_LIMIT
            )
            api_key_limit = settings.API_KEY_LIMITS.get(
                profile.plan_type, 
                settings.DEFAULT_API_KEY_LIMIT
            )

            current_workflows = Workflow.objects.filter(
                created_by=user, 
                is_active=True
            ).count()
            current_api_keys = APIKey.objects.filter(
                user=user, 
                is_active=True
            ).count()

            return Response({
                'plan': profile.plan_type,
                'limits': {
                    'workflows': {
                        'max': workflow_limit,
                        'used': current_workflows,
                        'remaining': workflow_limit - current_workflows
                    },
                    'api_keys': {
                        'max': api_key_limit,
                        'used': current_api_keys,
                        'remaining': api_key_limit - current_api_keys
                    }
                },
                'is_verified': user.is_verified,
                'account_created': user.date_joined,
                'last_login': user.last_login
            })
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch user limits'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )