from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.db import models
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from ..models.workspace import Workspace, WorkspaceMembership
from ..serializers.workspace import WorkspaceSerializer, WorkspaceMemberSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from ..models.activity import SecurityLog
from django.contrib.auth import get_user_model

class WorkspaceViewSet(viewsets.ModelViewSet):
    """View for Managing workspace"""
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return workspaces where user is either member or owner"""
        user = self.request.user
        print(f"\nDEBUG: Authenticated User ID: {user.id}")
        
        # Check owner workspaces
        owner_workspaces = Workspace.objects.filter(owner=user)
        print(f"DEBUG: Owner Workspaces: {owner_workspaces.count()}")
        for w in owner_workspaces:
            print(f"Owner Workspace: {w.id} - {w.name}")
        
        # Check member workspaces
        member_workspaces = Workspace.objects.filter(workspace_members__user=user)
        print(f"DEBUG: Member Workspaces: {member_workspaces.count()}")
        for w in member_workspaces:
            print(f"Member Workspace: {w.id} - {w.name}")
        
        # Get final queryset
        workspaces = Workspace.objects.filter(
            models.Q(owner=user) | 
            models.Q(workspace_members__user=user)
        ).distinct()
        
        print(f"DEBUG: Final Workspaces Count: {workspaces.count()}\n")
        
        return workspaces
    def perform_create(self, serializer):
        """Creating new workspace and adding current user as admin"""
        with transaction.atomic():
            workspace = serializer.save(owner=self.request.user)
            WorkspaceMembership.objects.create(
                user=self.request.user,
                workspace=workspace,
                role='admin',
                invited_by=self.request.user
            )
            
            
            SecurityLog.objects.create(
                user=self.request.user,
                action='workspace_created',
                details={
                    'workspace_id': str(workspace.id),
                    'workspace_name': workspace.name
                }
            )
            
    @swagger_auto_schema(
        operation_description="Get workspace statistics and limits",
        responses={
            200: openapi.Response(
                description="Workspace stats retrieved successfully",
                examples={
                    "application/json": {
                        "plan": "free",
                        "members": {
                            "total": 1,
                            "limit": 5
                        },
                        "teams": {
                            "total": 0,
                            "limit": 2
                        }
                    }
                }
            )
        }
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get workspace statistics and limits"""
        workspace = self.get_object()
        
        response_data = {
            'plan': workspace.plan_type,
            'members': {
                'total': workspace.workspace_members.count(),
                'limit': self._get_member_limit(workspace)
            },
            'teams': {
                'total': workspace.workspace_teams.count(),
                'limit': self._get_team_limit(workspace)
            }
        }
        
        return Response(response_data)
    
    @swagger_auto_schema(
        operation_description="Add member to workspace",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'role'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['admin', 'member']
                )
            }
        )
    )
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to workspace"""
        workspace = self.get_object()
        
        user_membership = workspace.workspace_members.filter(
            user=request.user
        ).first()
        
        if not user_membership or user_membership.role != 'admin':
            return Response(
                {'error': 'Only workspace admins can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        current_members = workspace.members.count()
        member_limit = self._get_member_limit(workspace)
        
        if current_members >= member_limit:
            return Response(
                {'error': f'Workspace member limit ({member_limit}) reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        email = request.data.get('email')
        role = request.data.get('role', 'member')
        
        try:
            User = get_user_model()
            user = User.objects.get(email=email)
            
            if workspace.workspace_members.filter(user=user).exists():
                return Response(
                    {'error': 'User is already a member of this workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            WorkspaceMembership.objects.create(
                user=user,
                workspace=workspace,
                role=role,
                invited_by=request.user
            )
            
            return Response({
                'message': f'Successfully added {user.email} to workspace'
            })

        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _get_member_limit(self, workspace):
        """Get member limit based on plan type"""
        limits = {
            'free': 5,
            'business': 20,
            'enterprise': 100
        }
        return limits.get(workspace.plan_type, 5)

    def _get_team_limit(self, workspace):
        """Get team limit based on plan type"""
        limits = {
            'free': 2,
            'business': 10,
            'enterprise': 50
        }
        return limits.get(workspace.plan_type, 2)