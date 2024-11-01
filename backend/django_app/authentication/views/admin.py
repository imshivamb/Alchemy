from datetime import datetime, timedelta
from django.db.models import Count, Q
from ..serializers import (
    UserExportSerializer,
    DetailedTeamSerializer,
    UserPlanUpdateSerializer
)
from ..models import UserProfile, SecurityLog ,TeamActivity, TeamMembership, Team
from .base import BaseViewSet
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminUserViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = UserExportSerializer
    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description="Get a list of all users with optional filters",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search in email, name, and organization",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_active', openapi.IN_QUERY,
                description="Filter by active status",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'plan_type', openapi.IN_QUERY,
                description="Filter by plan type",
                type=openapi.TYPE_STRING,
                enum=['free', 'basic', 'premium', 'enterprise']
            ),
        ],
        responses={
            200: UserExportSerializer(many=True),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Users']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve user details",
        operation_description="Get detailed information about a specific user",
        responses={
            200: UserExportSerializer,
            404: 'User not found',
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Users']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update user plan",
        operation_description="Update a user's subscription plan",
        request_body=UserPlanUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Plan updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'old_plan': openapi.Schema(type=openapi.TYPE_STRING),
                        'new_plan': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: 'Invalid plan type',
            403: 'Forbidden - Admin access required',
            404: 'User not found'
        },
        tags=['Admin - Users']
    )
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Apply filters
        filters = {}
        
        if self.request.query_params.get('is_active'):
            filters['is_active'] = self.request.query_params['is_active'] == 'true'
            
        if self.request.query_params.get('plan_type'):
            filters['profile__plan_type'] = self.request.query_params['plan_type']
            
        if self.request.query_params.get('joined_after'):
            filters['date_joined__gte'] = self.request.query_params['joined_after']
            
        # Apply search
        search = self.request.query_params.get('search')
        if search:
            return queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(organization__icontains=search)
            ).filter(**filters)
            
        return queryset.filter(**filters)

    @action(detail=True, methods=['post'])
    def update_plan(self, request, pk=None):
        user = self.get_object()
        serializer = UserPlanUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            old_plan = user.profile.plan_type
            new_plan = serializer.validated_data['plan_type']
            
            user.profile.plan_type = new_plan
            user.profile.save()
            
            # Log plan change
            SecurityLog.objects.create(
                user=user,
                action='plan_updated',
                details={
                    'old_plan': old_plan,
                    'new_plan': new_plan,
                    'updated_by': request.user.id
                }
            )
            
            return Response({
                'message': 'Plan updated successfully',
                'user_id': str(user.id),
                'old_plan': old_plan,
                'new_plan': new_plan
            })
            
        return Response(serializer.errors, status=400)

class AdminTeamViewSet(BaseViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = DetailedTeamSerializer
    @swagger_auto_schema(
        operation_summary="List all teams",
        operation_description="Get a list of all teams with optional filters",
        manual_parameters=[
            openapi.Parameter(
                'owner_id', openapi.IN_QUERY,
                description="Filter by team owner ID",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: DetailedTeamSerializer(many=True),
            403: 'Forbidden - Admin access required'
        },
        tags=['Admin - Teams']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Transfer team ownership",
        operation_description="Transfer ownership of a team to another user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_owner_id'],
            properties={
                'new_owner_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='UUID of the new owner'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Ownership transferred successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous_owner': openapi.Schema(type=openapi.TYPE_STRING),
                        'new_owner': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: 'Invalid request',
            403: 'Forbidden - Admin access required',
            404: 'Team not found'
        },
        tags=['Admin - Teams']
    )
    def get_queryset(self):
        queryset = Team.objects.all()
        
        # Apply filters
        if self.request.query_params.get('owner_id'):
            queryset = queryset.filter(
                owner_id=self.request.query_params['owner_id']
            )
            
        if self.request.query_params.get('created_after'):
            queryset = queryset.filter(
                created_at__gte=self.request.query_params['created_after']
            )
            
        return queryset

    @action(detail=True, methods=['post'])
    def transfer_ownership(self, request, pk=None):
        team = self.get_object()
        new_owner_id = request.data.get('new_owner_id')
        
        try:
            new_owner = User.objects.get(id=new_owner_id)
            old_owner = team.owner
            
            team.owner = new_owner
            team.save()
            
            # Update memberships
            TeamMembership.objects.filter(
                team=team,
                user=new_owner
            ).update(role='admin')
            
            # Log ownership transfer
            TeamAuditLog.objects.create(
                team=team,
                user=request.user,
                action='ownership_transferred',
                changes={
                    'old_owner': str(old_owner.id),
                    'new_owner': str(new_owner.id)
                }
            )
            
            return Response({
                'message': 'Ownership transferred successfully',
                'previous_owner': str(old_owner.id),
                'new_owner': str(new_owner.id)
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'New owner not found'},
                status=status.HTTP_404_NOT_FOUND
            )