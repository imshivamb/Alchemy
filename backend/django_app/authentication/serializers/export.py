# serializers/export.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .team import TeamMembershipDetailSerializer
from .activity import UserActivitySerializer

User = get_user_model()

class UserExportSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for exporting user data
    Includes detailed user information, teams, profile, and activity
    """
    teams = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    activity_summary = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'first_name',
            'last_name',
            'organization',
            'is_active',
            'is_verified',
            'created_at',
            'last_login',
            'teams',
            'profile',
            'activity_summary'
        ]
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email
        
    def get_teams(self, obj):
        """Get all teams user is member of with role information"""
        memberships = obj.team_memberships.select_related('team').all()
        return [{
            'team_name': membership.team.name,
            'role': membership.role,
            'joined_at': membership.joined_at,
            'is_owner': membership.team.owner_id == obj.id
        } for membership in memberships]
        
    def get_profile(self, obj):
        """Get user profile information"""
        return {
            'plan_type': obj.profile.plan_type,
            'max_workflows': obj.profile.max_workflows,
            'timezone': obj.profile.timezone,
            'notification_preferences': obj.profile.notification_preferences,
            'account_status': obj.profile.account_status,
            'onboarding_completed': obj.profile.onboarding_completed
        }
        
    def get_activity_summary(self, obj):
        """Get recent user activities"""
        recent_activities = obj.activities.all()[:5]
        return UserActivitySerializer(recent_activities, many=True).data


