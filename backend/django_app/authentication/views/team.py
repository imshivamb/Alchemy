from ..models import Team, TeamMembership, TeamActivity, Workspace, User
from ..serializers.team import (
    TeamSerializer, 
    TeamMembershipDetailSerializer,
    DetailedTeamSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .base import BaseViewSet
from django.db import models

class TeamViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on the action"""
        if self.action == 'retrieve':
            return DetailedTeamSerializer
        elif self.action == 'list':
            return TeamSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TeamSerializer
        elif self.action == 'add_member':
            return TeamMembershipDetailSerializer
            
        return TeamSerializer

    def get_queryset(self):
        """Optimized queryset based on action"""
        workspace_id = self.request.query_params.get('workspace')
        
        if not workspace_id:
            raise ValidationError({'workspace': 'Workspace ID is required'})

        queryset = Team.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members=self.request.user),
            workspace_id=workspace_id,
            workspace__members=self.request.user,
        ).distinct()

        if self.action == 'retrieve':
            return queryset.select_related('owner').prefetch_related(
                'members',
                'memberships',
                'memberships__user'
            )
        elif self.action == 'list':
            return queryset.select_related('owner')
            
        return queryset

    @swagger_auto_schema(
        operation_summary="List teams",
        operation_description="Get list of teams user belongs to",
        manual_parameters=[
            openapi.Parameter(
                'workspace',
                openapi.IN_QUERY,
                description="Workspace ID (required)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: TeamSerializer(many=True)},
        tags=['Teams']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create team",
        operation_description="Create a new team",
        request_body=TeamSerializer,
        responses={201: TeamSerializer},
        tags=['Teams']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get team details",
        operation_description="Get detailed information about a specific team",
        responses={
            200: DetailedTeamSerializer,
            404: 'Team not found'
        },
        tags=['Teams']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update team",
        operation_description="Update team details (requires admin permission)",
        request_body=TeamSerializer,
        responses={
            200: TeamSerializer,
            403: 'Only team admins can update team',
            404: 'Team not found'
        },
        tags=['Teams']
    )
    def update(self, request, *args, **kwargs):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, role='admin').exists():
            return Response(
                {'error': 'Only team admins can update team'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update team",
        operation_description="Partially update team details (requires admin permission)",
        request_body=TeamSerializer,
        responses={
            200: TeamSerializer,
            403: 'Only team admins can update team',
            404: 'Team not found'
        },
        tags=['Teams']
    )
    def partial_update(self, request, *args, **kwargs):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, role='admin').exists():
            return Response(
                {'error': 'Only team admins can update team'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete team",
        operation_description="Delete team (requires admin permission)",
        responses={
            204: 'Team deleted successfully',
            403: 'Only team admins can delete team',
            404: 'Team not found'
        },
        tags=['Teams']
    )
    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, role='admin').exists():
            return Response(
                {'error': 'Only team admins can delete team'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        TeamActivity.objects.create(
            team=team,
            user=request.user,
            action='team_deleted',
            details={
                'team_name': team.name,
                'workspace_id': str(team.workspace.id)
            }
        )
        
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add team member",
        operation_description="Add a new member to the team",
        methods=['post'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id', 'role'],
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User ID to add'
                ),
                'role': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['admin', 'editor', 'viewer'],
                    description='Role for the new member'
                )
            }
        ),
        responses={
            200: TeamMembershipDetailSerializer,
            400: 'Invalid request data',
            403: 'Only team admins can add members',
            404: 'Team not found'
        },
        tags=['Teams']
    )
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to team with workspace validation"""
        team = self.get_object()
        if not team.memberships.filter(user=request.user, role='admin').exists():
            return Response(
                {'error': 'Only team admins can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        try:
            user_to_add = User.objects.get(id=user_id)
            
            # Check if user is workspace member
            if not team.workspace.members.filter(id=user_to_add.id).exists():
                return Response(
                    {'error': 'User must be a workspace member to join team'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check team member limit
            if team.members.count() >= team.max_members:
                return Response(
                    {'error': 'Team member limit reached'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            membership = TeamMembership.objects.create(
                user=user_to_add,
                team=team,
                role=request.data.get('role', 'viewer')
            )
            
            TeamActivity.objects.create(
                team=team,
                user=request.user,
                action='member_added',
                details={
                    'added_user_id': str(user_to_add.id),
                    'role': membership.role
                }
            )
            
            return Response(TeamMembershipDetailSerializer(membership).data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def perform_create(self, serializer):
        """Create new team within workspace after validations"""
        workspace_id = self.request.data.get('workspace')
        if not workspace_id:
            raise ValidationError("Workspace ID is required")
            
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            
            # Check if user is workspace member
            if not workspace.members.filter(id=self.request.user.id).exists():
                raise PermissionDenied("Must be a workspace member to create team")
            
            # Check workspace team limit
            current_teams = workspace.workspace_teams.count()
            team_limit = {
                'free': 2,
                'business': 10,
                'enterprise': 50
            }.get(workspace.plan_type, 2)
            
            if current_teams >= team_limit:
                raise ValidationError(f"Workspace team limit ({team_limit}) reached")
            
            # Create team
            team = serializer.save(
                owner=self.request.user,
                workspace=workspace
            )
            
            # Add creator as admin
            TeamMembership.objects.create(
                user=self.request.user,
                team=team,
                role='admin'
            )
            
            # Log activity
            TeamActivity.objects.create(
                team=team,
                user=self.request.user,
                action='team_created',
                details={
                    'workspace_id': str(workspace.id),
                    'team_name': team.name
                }
            )
            
        except Workspace.DoesNotExist:
            raise NotFound("Workspace not found")