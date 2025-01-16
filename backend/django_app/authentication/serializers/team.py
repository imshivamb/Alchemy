from .base import TimestampedSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.conf import settings
from django.db import models
from ..models import Team, TeamMembership, Workspace

User = get_user_model()

class TeamMembershipDetailSerializer(TimestampedSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'role', 'joined_at', 'created_at', 'updated_at']
        
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'name': f"{obj.user.first_name} {obj.user.last_name}".strip(),
            'is_active': obj.user.is_active
        }

class TeamSerializer(TimestampedSerializer):
    members_count = serializers.SerializerMethodField()
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    workspace = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 
            'name', 
            'description', 
            'owner_email',
            'members_count',
            'workspace',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['owner_email', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': False},
            'workspace': {'write_only': True}
        }
    
    def get_members_count(self, obj):
        return obj.members.count()

    def validate(self, attrs):
        request = self.context['request']
        if request.method == 'POST':
            if 'name' not in attrs:
                raise serializers.ValidationError({'name': 'This field is required.'})
            
            user = request.user
            if not user.profile.is_paid_plan:
                teams_count = user.owned_teams.count()
                if teams_count >= settings.FREE_PLAN_TEAM_LIMIT:
                    raise serializers.ValidationError(
                        "Free plan users can only create up to "
                        f"{settings.FREE_PLAN_TEAM_LIMIT} teams."
                    )
        return attrs

    def update(self, instance, validated_data):
        workspace_uuid = validated_data.pop('workspace', None)
        if workspace_uuid:
            try:
                # Fetch the Workspace instance
                workspace = Workspace.objects.get(id=workspace_uuid)
                validated_data['workspace'] = workspace
            except Workspace.DoesNotExist:
                raise serializers.ValidationError({'workspace': 'Invalid workspace ID provided.'})
        
        # Proceed with the default update logic
        return super().update(instance, validated_data)



class DetailedTeamSerializer(TeamSerializer):
    members = TeamMembershipDetailSerializer(
        source='memberships',
        many=True,
        read_only=True
    )
    statistics = serializers.SerializerMethodField()
    
    class Meta(TeamSerializer.Meta):
        model = Team
        fields = TeamSerializer.Meta.fields + ['members', 'statistics']
        
    def get_statistics(self, obj):
        return {
            'total_members': obj.members.count(),
            'active_members': obj.members.filter(is_active=True).count(),
            'roles_distribution': obj.memberships.values('role').annotate(
                count=models.Count('id')
            )
        }
