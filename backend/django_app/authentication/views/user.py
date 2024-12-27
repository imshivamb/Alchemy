from ..serializers.profile import UserProfileSerializer
from ..serializers.auth import UserSerializer
from ..models import UserProfile, SecurityLog, APIKey
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
from workflow_engine.models import Workflow
from django.contrib.auth import get_user_model
from .base import BaseViewSet


User = get_user_model()
class UserViewSet(BaseViewSet):
    """
    ViewSet for user-related operations.
    Provides CRUD operations for users with appropriate permissions.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions:
        - Staff users can see all users
        - Regular users can only see themselves
        """
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @swagger_auto_schema(
        operation_description="Generate new API key for user",
        responses={
            200: openapi.Response(
                description="API key generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'key': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['post'])
    def generate_api_key(self, request, pk=None):
        """Generate a new API key for the user"""
        user = self.get_object()
        
        # Check if user has reached API key limit
        current_keys = APIKey.objects.filter(
            user=user,
            is_active=True
        ).count()
        
        max_keys = user.profile.get_api_key_limit()
        
        if current_keys >= max_keys:
            return Response(
                {
                    'error': f'Maximum number of API keys ({max_keys}) reached'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate new API key
        with transaction.atomic():
            api_key = APIKey.objects.create(
                user=user,
                name=f"API Key - {uuid.uuid4().hex[:8]}",
                key=uuid.uuid4().hex,
                scopes=['read', 'write']  # Default scopes
            )
            
            # Log API key generation
            SecurityLog.objects.create(
                user=user,
                action='api_key_generated',
                details={
                    'key_name': api_key.name,
                    'key_id': str(api_key.id)
                }
            )
        
        return Response({
            'key': api_key.key,
            'name': api_key.name
        })

    @swagger_auto_schema(
        operation_description="Update user profile picture",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'profile_picture': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='binary'
                )
            }
        ),
        responses={
            200: "Profile picture updated successfully",
            400: "Invalid image format"
        }
    )
    @action(detail=True, methods=['post'], url_path='profile-picture')
    def update_profile_picture(self, request, pk=None):
        """Update user's profile picture"""
        import os
        from django.conf import settings
        from datetime import datetime

        user = self.get_object()
        
        if 'profile_picture' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Create dynamic path based on current date
            current_date = datetime.now()
            upload_path = os.path.join(
                settings.MEDIA_ROOT,
                'profile_pics',
                str(current_date.year),
                str(current_date.month).zfill(2)
            )
            
            # Create directories if they don't exist
            os.makedirs(upload_path, exist_ok=True)
            
            # Now handle the file upload
            user.profile_picture = request.FILES['profile_picture']
            user.save()
            
            return Response({
                'message': 'Profile picture updated successfully',
                'profile_picture_url': user.profile_picture.url
            })
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error updating profile picture: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Get user's activity history",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description="User activity history",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'action': openapi.Schema(type=openapi.TYPE_STRING),
                                    'details': openapi.Schema(type=openapi.TYPE_OBJECT),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                                }
                            )
                        )
                    }
                )
            )
        }
    )
    @action(detail=True, methods=['get'])
    def activity_history(self, request, pk=None):
        """Get user's activity history"""
        user = self.get_object()
        
        activities = SecurityLog.objects.filter(user=user).order_by('-created_at')
        
        # Pagination
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate user account"""
        user = self.get_object()
        
        if user == request.user or request.user.is_staff:
            with transaction.atomic():
                user.is_active = False
                user.save()
                
                # Log account deactivation
                SecurityLog.objects.create(
                    user=user,
                    action='account_deactivated',
                    details={
                        'deactivated_by': str(request.user.id),
                        'reason': request.data.get('reason', 'User requested')
                    }
                )
                
            return Response({
                'message': 'Account deactivated successfully'
            })
            
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate user account (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff access required'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        user = self.get_object()
        
        with transaction.atomic():
            user.is_active = True
            user.save()
            
            # Log account reactivation
            SecurityLog.objects.create(
                user=user,
                action='account_reactivated',
                details={
                    'reactivated_by': str(request.user.id),
                    'reason': request.data.get('reason', 'Staff action')
                }
            )
            
        return Response({
            'message': 'Account reactivated successfully'
        })
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    @swagger_auto_schema(
        operation_description="Get current user's profile details",
        responses={200: UserSerializer}
    )
    def get(self, request):
        """Get current user's profile details"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update current user's profile",
        request_body=UserProfileSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request):
        """Update current user's profile"""
        user_serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if user_serializer.is_valid():
            user_serializer.save()
            
            # Log profile update
            SecurityLog.objects.create(
                user=request.user,
                action='profile_updated',
                details={'updated_fields': request.data.keys()}
            )
            
            return Response(user_serializer.data)
            
        return Response(user_serializer.errors, status=400)
    
class UserLimitsView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @swagger_auto_schema(
        operation_description="Get user's current usage limits and statistics",
        responses={
            200: openapi.Response(
                description="User limits retrieved successfully",
                examples={
                    "application/json": {
                        "plan": "free",
                        "limits": {
                            "workflows": {
                                "max": 10,
                                "used": 3,
                                "remaining": 7
                            },
                            "api_keys": {
                                "max": 5,
                                "used": 1,
                                "remaining": 4
                            }
                        },
                        "is_verified": True,
                        "account_created": "2024-01-01T00:00:00Z",
                        "last_login": "2024-01-02T00:00:00Z"
                    }
                }
            )
        }
    )
    def get(self, request):
        try:
            user = request.user
            profile = user.profile

            # Get limits from settings
            workflow_limit = settings.WORKFLOW_LIMITS.get(
                profile.plan_type, 
                settings.DEFAULT_WORKFLOW_LIMIT
            )
            api_key_limit = settings.API_KEY_LIMITS.get(
                profile.plan_type, 
                settings.DEFAULT_API_KEY_LIMIT
            )

            # Get current usage
            current_workflows = Workflow.objects.filter(
                created_by=user, 
                is_active=True
            ).count()
            current_api_keys = APIKey.objects.filter(
                user=user, 
                is_active=True
            ).count()

            response_data = {
                'plan': profile.plan_type,
                'limits': {
                    'workflows': {
                        'max': workflow_limit,
                        'used': current_workflows,
                        'remaining': max(0, workflow_limit - current_workflows)
                    },
                    'api_keys': {
                        'max': api_key_limit,
                        'used': current_api_keys,
                        'remaining': max(0, api_key_limit - current_api_keys)
                    }
                },
                'is_verified': user.is_verified,
                'account_created': user.created_at,
                'last_login': user.last_login,
                'profile_status': {
                    'onboarding_completed': profile.onboarding_completed,
                    'account_status': profile.account_status
                }
            }

            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': 'Failed to fetch user limits'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )