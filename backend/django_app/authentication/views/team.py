from ..models import Team, TeamMembership, TeamActivity
from ..serializers.team import (
    TeamSerializer, 
    DetailedTeamSerializer,
    TeamMembershipDetailSerializer,
    
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .base import BaseViewSet
from django.db import models

class TeamViewSet(BaseViewSet):
    serializer_class = TeamSerializer
    
    @swagger_auto_schema(
        operation_summary="List teams",
        operation_description="Get list of teams user belongs to",
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
            200: TeamSerializer,
            404: 'Team not found'
        },
        tags=['Teams']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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
        # Existing implementation remains the same
        team = self.get_object()
        
        if not team.memberships.filter(user=request.user, role='admin').exists():
            return Response(
                {'error': 'Only team admins can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = TeamMembershipSerializer(data={
            'user': request.data.get('user_id'),
            'team': team.id,
            'role': request.data.get('role', 'viewer')
        })
        
        if serializer.is_valid():
            membership = serializer.save()
            
            TeamActivity.objects.create(
                team=team,
                user=request.user,
                action='member_added',
                details={
                    'added_user_id': str(membership.user.id),
                    'role': membership.role
                }
            )
            
            return Response(serializer.data)
            
        return Response(serializer.errors, status=400)

    def get_queryset(self):
        return Team.objects.filter(
            models.Q(members=self.request.user) | 
            models.Q(owner=self.request.user)
        ).distinct()
        
    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        
        TeamMembership.objects.create(
            user=self.request.user,
            team=team,
            role='admin'
        )
        
        TeamActivity.objects.create(
            team=team,
            user=self.request.user,
            action='team_created'
        )