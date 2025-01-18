from rest_framework import serializers
from ..models import Workspace, SecurityLog
from .auth import UserSerializer
from .team import TeamSerializer

class DetailedWorkspaceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    team_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'owner', 'plan_type', 
            'settings', 'member_count', 'team_count',
            'created_at', 'updated_at'
        ]

class SecurityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = SecurityLog
        fields = [
            'id', 'user_email', 'action', 'severity',
            'details', 'is_resolved', 'resolution_notes',
            'ip_address', 'created_at'
        ]

class SystemHealthSerializer(serializers.Serializer):
    database_status = serializers.CharField()
    cache_status = serializers.CharField()
    storage_status = serializers.CharField()
    last_error = serializers.CharField(allow_null=True)
    system_metrics = serializers.DictField()

class AnalyticsOverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_workspaces = serializers.IntegerField()
    total_teams = serializers.IntegerField()
    plan_distribution = serializers.DictField()
    user_growth = serializers.ListField()