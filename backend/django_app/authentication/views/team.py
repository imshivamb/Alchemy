from ..models import Team, TeamMembership, TeamActivity
from ..serializers.team import (
    TeamSerializer, 
    DetailedTeamSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .base import BaseViewSet
from django.db import models

class TeamViewSet(BaseViewSet):
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        return Team.objects.filter(
            models.Q(members=self.request.user) | 
            models.Q(owner=self.request.user)
        ).distinct()
        
    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        
        # Create admin membership for owner
        TeamMembership.objects.create(
            user=self.request.user,
            team=team,
            role='admin'
        )
        
        # Log team creation
        TeamActivity.objects.create(
            team=team,
            user=self.request.user,
            action='team_created'
        )
        
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        team = self.get_object()
        
        # Check if user has admin permissions
        if not team.memberships.filter(
            user=request.user, 
            role='admin'
        ).exists():
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
            
            # Log member addition
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