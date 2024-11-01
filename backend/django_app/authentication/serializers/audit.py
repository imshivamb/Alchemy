from rest_framework import serializers
from django.contrib.auth import get_user_model
from .base import TimestampedSerializer
from ..models import TeamActivity

User = get_user_model()

class TeamAuditLogSerializer(TimestampedSerializer):
    """
    Serializer for team audit logs with detailed change tracking
    """
    user = serializers.SerializerMethodField()
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = TeamActivity
        fields = [
            'id',
            'team_name',
            'user',
            'action',
            'details', 
            'created_at',
            'updated_at'
        ]

    def get_user(self, obj):
        if not obj.user:
            return None

        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'name': f"{obj.user.first_name} {obj.user.last_name}".strip(),
            'is_active': obj.user.is_active
        }

    def to_representation(self, instance):
        """Enhanced representation with formatted details"""
        data = super().to_representation(instance)
        
        # Format the details log for better readability
        if data['details']:
            formatted_details = {}
            for field, change in data['details'].items():
                if isinstance(change, dict) and 'old' in change and 'new' in change:
                    formatted_details[field] = {
                        'from': change['old'],
                        'to': change['new']
                    }
            data['details'] = formatted_details

        return data