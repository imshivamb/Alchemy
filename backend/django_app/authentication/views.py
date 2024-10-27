from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
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
from django.db.models import Count, Q
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Team, TeamMembership, APIKey, UserProfile, LoginHistory, TeamActivity, TeamAuditLog, UserActivity
from workflow_engine.models import Workflow
from .serializers import (
    UserSerializer, 
    TeamSerializer, 
    TeamMembershipSerializer,
    EmailVerificationSerializer,
    PasswordResetSerializer,
    APIKeySerializer,
    UserActivitySerializer,
    UserExportSerializer,
    ActivitySerializer,
    TeamAuditLogSerializer,
    UserPlanUpdateSerializer,
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
    
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get current user's profile details",
        responses={
            200: openapi.Response(
                description="User details retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'organization': openapi.Schema(type=openapi.TYPE_STRING),
                        'profile': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'plan_type': openapi.Schema(type=openapi.TYPE_STRING),
                                'timezone': openapi.Schema(type=openapi.TYPE_STRING),
                                'notification_preferences': openapi.Schema(type=openapi.TYPE_OBJECT),
                                'max_workflows': openapi.Schema(type=openapi.TYPE_INTEGER),
                            }
                        )
                    }
                )
            )
        }
    )
    def get(self, request):
        """Get current user's profile details"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update current user's profile",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User's first name"
                ),
                'last_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User's last name"
                ),
                'organization': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User's organization"
                ),
                'profile': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'timezone': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="User's timezone (e.g., 'UTC', 'America/New_York')"
                        ),
                        'notification_preferences': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="User's notification settings",
                            properties={
                                'email_notifications': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'workflow_notifications': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'team_notifications': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                            }
                        )
                    }
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'organization': openapi.Schema(type=openapi.TYPE_STRING),
                        'profile': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'plan_type': openapi.Schema(type=openapi.TYPE_STRING),
                                'timezone': openapi.Schema(type=openapi.TYPE_STRING),
                                'notification_preferences': openapi.Schema(type=openapi.TYPE_OBJECT),
                                'max_workflows': openapi.Schema(type=openapi.TYPE_INTEGER),
                            }
                        )
                    }
                )
            ),
            400: "Bad Request - Invalid data provided",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Insufficient permissions"
        }
    )
    def patch(self, request):
        """Update current user's profile"""
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
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
    """
    ViewSet for handling team operations
    Provides: list, create, retrieve, update, delete
    Plus custom actions: add_member, remove_member, update_member_role
    """
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)
        
    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        # Automatically add creator as admin
        TeamMembership.objects.create(
            user=self.request.user,
            team=team,
            role='admin'
        )
        
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to team"""
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
            TeamMembership.objects.create(
                user=user,
                team=team,
                role=role
            )
            return Response({'status': 'member added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove member from team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            membership = TeamMembership.objects.get(
                team=team,
                user_id=user_id
            )
            membership.delete()
            return Response({'status': 'member removed'})
        except TeamMembership.DoesNotExist:
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    @action(detail=True, methods=['post'])
    def update_member_role(self, request, pk=None):
        """Update team member's role"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        if not all([user_id, new_role]):
            return Response(
                {'error': 'user_id and role are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            membership = TeamMembership.objects.get(
                team=team,
                user_id=user_id
            )
            membership.role = new_role
            membership.save()
            return Response({'status': 'role updated'})
        except TeamMembership.DoesNotExist:
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members list"""
        team = self.get_object()
        memberships = TeamMembership.objects.filter(team=team)
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
            
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
            
class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for user management
    Provides complete control over all users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="List all users with filtering options",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search users by email, name, or organization",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filter by active status",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'plan_type',
                openapi.IN_QUERY,
                description="Filter by plan type",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Activate user account",
        responses={
            200: openapi.Response(
                description="User activated successfully",
                examples={
                    "application/json": {
                        "message": "User activated successfully",
                        "user_id": "uuid"
                    }
                }
            )
        }
    )

    def get_queryset(self):
        """
        Filter users based on query parameters
        """
        queryset = User.objects.all()
        
        # Search users
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(organization__icontains=search)
            )
            
        # Filter by status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
            
        # Filter by plan type
        plan_type = self.request.query_params.get('plan_type', None)
        if plan_type:
            queryset = queryset.filter(profile__plan_type=plan_type)
            
        # Filter by date joined
        joined_after = self.request.query_params.get('joined_after', None)
        if joined_after:
            queryset = queryset.filter(date_joined__gte=joined_after)
            
        return queryset

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate user account
        POST /api/v1/admin/users/{id}/activate/
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'message': 'User activated successfully',
            'user_id': user.id
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate user account
        POST /api/v1/admin/users/{id}/deactivate/
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response({
            'message': 'User deactivated successfully',
            'user_id': user.id
        })

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Reset user password
        POST /api/v1/admin/users/{id}/reset_password/
        """
        user = self.get_object()
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.set_password(password)
        user.save()
        
        return Response({
            'message': 'Password reset successfully',
            'user_id': user.id
        })

    @action(detail=True, methods=['post'])
    def update_plan(self, request, pk=None):
        """
        Update user plan
        POST /api/v1/admin/users/{id}/update_plan/
        """
        user = self.get_object()
        plan_type = request.data.get('plan_type')
        
        if not plan_type:
            return Response(
                {'error': 'Plan type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.profile.plan_type = plan_type
        user.profile.save()
        
        return Response({
            'message': 'Plan updated successfully',
            'user_id': user.id,
            'new_plan': plan_type
        })

    @action(detail=True, methods=['get'])
    def activity_log(self, request, pk=None):
        """
        Get user activity log
        GET /api/v1/admin/users/{id}/activity_log/
        """
        user = self.get_object()
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        activities = UserActivity.objects.filter(
            user=user,
            timestamp__gte=start_date
        ).order_by('-timestamp')
        
        return Response(UserActivitySerializer(activities, many=True).data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get user statistics
        GET /api/v1/admin/users/{id}/statistics/
        """
        user = self.get_object()
        
        stats = {
            'workflows_count': user.workflow_set.count(),
            'teams_count': user.teams.count(),
            'api_keys_count': user.api_keys.count(),
            'last_login': user.last_login,
            'account_age_days': (datetime.now().date() - user.date_joined.date()).days,
            'teams': list(user.teams.values('id', 'name', 'role')),
            'recent_activities': UserActivitySerializer(
                user.activities.order_by('-timestamp')[:5],
                many=True
            ).data
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get users overview
        GET /api/v1/admin/users/overview/
        """
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        overview = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'users_by_plan': User.objects.values(
                'profile__plan_type'
            ).annotate(
                count=Count('id')
            ),
            'recent_registrations': UserSerializer(
                User.objects.order_by('-date_joined')[:5],
                many=True
            ).data,
            'recent_logins': UserSerializer(
                User.objects.exclude(
                    last_login=None
                ).order_by('-last_login')[:5],
                many=True
            ).data
        }
        
        return Response(overview)

    @action(detail=False, methods=['get'])
    def export_users(self, request):
        """
        Export users data
        GET /api/v1/admin/users/export_users/
        """
        users = User.objects.all()
        data = UserExportSerializer(users, many=True).data
        
        return Response({
            'count': len(data),
            'users': data
        })

    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """
        Bulk activate users
        POST /api/v1/admin/users/bulk_activate/
        """
        user_ids = request.data.get('user_ids', [])
        
        updated = User.objects.filter(
            id__in=user_ids
        ).update(is_active=True)
        
        return Response({
            'message': f'{updated} users activated successfully',
            'affected_users': user_ids
        })
        
    @swagger_auto_schema(
        operation_description="Update user's plan type",
        request_body=UserPlanUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Plan updated successfully",
                examples={
                    "application/json": {
                        "message": "Plan updated successfully",
                        "user_id": "uuid",
                        "previous_plan": "free",
                        "new_plan": "premium"
                    }
                }
            ),
            400: "Invalid plan type",
            404: "User not found",
            403: "Not authorized to update plans"
        },
        operation_summary="Update user plan",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="User ID",
                type=openapi.TYPE_STRING,
                format="uuid",
                required=True
            )
        ]
    )
    @action(detail=True, methods=['post'])
    def update_plan(self, request, pk=None):
        """
        Update user's plan type
        """
        user = self.get_object()
        serializer = UserPlanUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            previous_plan = user.profile.plan_type
            new_plan = serializer.validated_data['plan_type']
            
            # Update the plan
            user.profile.plan_type = new_plan
            user.profile.save()
            
            # Log the plan change
            UserActivity.objects.create(
                user=user,
                action="plan_updated",
                details={
                    "previous_plan": previous_plan,
                    "new_plan": new_plan,
                    "updated_by": request.user.id
                }
            )
            
            return Response({
                "message": "Plan updated successfully",
                "user_id": str(user.id),
                "previous_plan": previous_plan,
                "new_plan": new_plan
            })
            
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def bulk_update_plan(self, request):
        """
        Bulk update user plans
        POST /api/v1/admin/users/bulk_update_plan/
        """
        user_ids = request.data.get('user_ids', [])
        plan_type = request.data.get('plan_type')
        
        if not plan_type:
            return Response(
                {'error': 'Plan type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        updated = User.objects.filter(
            id__in=user_ids
        ).update(profile__plan_type=plan_type)
        
        return Response({
            'message': f'{updated} users updated to {plan_type} plan',
            'affected_users': user_ids
        })
        
        
class AdminTeamViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for team management
    Provides complete control over all teams
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Allow filtering teams
        """
        queryset = Team.objects.all()
        
        # Filter by owner
        owner_id = self.request.query_params.get('owner_id', None)
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
            
        # Filter by member
        member_id = self.request.query_params.get('member_id', None)
        if member_id:
            queryset = queryset.filter(members__id=member_id)
            
        # Filter by creation date
        created_after = self.request.query_params.get('created_after', None)
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
            
        return queryset

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get team statistics
        GET /api/v1/admin/teams/{id}/statistics/
        """
        team = self.get_object()
        
        # Calculate statistics
        stats = {
            'total_members': team.members.count(),
            'member_roles': TeamMembership.objects.filter(team=team)
                .values('role')
                .annotate(count=Count('id')),
            'active_members': team.members.filter(is_active=True).count(),
            'last_activity': team.updated_at,
        }
        
        return Response(stats)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """
        Get team activity log
        GET /api/v1/admin/teams/{id}/activities/
        """
        team = self.get_object()
        
        # Get activities from your activity tracking system
        activities = TeamActivity.objects.filter(team=team)
        return Response(ActivitySerializer(activities, many=True).data)

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get overview of all teams
        GET /api/v1/admin/teams/overview/
        """
        overview = {
            'total_teams': Team.objects.count(),
            'teams_by_size': Team.objects.annotate(
                member_count=Count('members')
            ).values('member_count').annotate(
                team_count=Count('id')
            ),
            'recent_teams': TeamSerializer(
                Team.objects.order_by('-created_at')[:5],
                many=True
            ).data,
        }
        
        return Response(overview)

    @action(detail=True, methods=['post'])
    def transfer_ownership(self, request, pk=None):
        """
        Transfer team ownership
        POST /api/v1/admin/teams/{id}/transfer_ownership/
        """
        team = self.get_object()
        new_owner_id = request.data.get('new_owner_id')
        
        try:
            new_owner = User.objects.get(id=new_owner_id)
            old_owner = team.owner
            
            # Update team owner
            team.owner = new_owner
            team.save()
            
            # Update memberships
            TeamMembership.objects.filter(
                team=team,
                user=new_owner
            ).update(role='admin')
            
            return Response({
                'message': 'Ownership transferred successfully',
                'previous_owner': str(old_owner),
                'new_owner': str(new_owner)
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'New owner not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive/Unarchive team
        POST /api/v1/admin/teams/{id}/archive/
        """
        team = self.get_object()
        archive = request.data.get('archive', True)
        
        team.is_archived = archive
        team.archived_at = datetime.now() if archive else None
        team.save()
        
        return Response({
            'message': f"Team {'archived' if archive else 'unarchived'} successfully"
        })

    @action(detail=False, methods=['get'])
    def audit_log(self, request):
        """
        Get team audit log
        GET /api/v1/admin/teams/audit_log/
        """
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        audit_logs = TeamAuditLog.objects.filter(
            timestamp__gte=start_date
        ).order_by('-timestamp')
        
        return Response(TeamAuditLogSerializer(audit_logs, many=True).data)