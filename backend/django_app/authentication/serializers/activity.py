from .base import TimestampedSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import UserActivity, TeamActivity 

User = get_user_model()

class BaseActivitySerializer(TimestampedSerializer):
    """Base serializer for activity logging"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        abstract = True
        fields = [
            'id',
            'user_email',
            'action',
            'details',
            'created_at'
        ]

class UserActivitySerializer(BaseActivitySerializer):
    """Serializer for user-specific activities"""
    class Meta(BaseActivitySerializer.Meta):
        model = UserActivity  # Use the imported model directly
        fields = BaseActivitySerializer.Meta.fields + ['ip_address']

class TeamActivitySerializer(BaseActivitySerializer):
    """Serializer for team-related activities"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta(BaseActivitySerializer.Meta):
        model = TeamActivity  # Use the imported model directly
        fields = BaseActivitySerializer.Meta.fields + ['team_name']