from .base import TimestampedSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.conf import settings
from django.db import models

User = get_user_model()

class APIKeySerializer(TimestampedSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = User.api_keys.field.related_model
        fields = [
            'id', 
            'user', 
            'name', 
            'key', 
            'is_active',
            'scopes',
            'rate_limit', 
            'expires_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['key', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        user = self.context['request'].user
        if not attrs.get('is_active', True):
            return attrs
            
        current_active_keys = user.api_keys.filter(is_active=True).count()
        max_allowed = settings.API_KEY_LIMITS.get(
            user.profile.plan_type, 
            settings.DEFAULT_API_KEY_LIMIT
        )
        
        if current_active_keys >= max_allowed:
            raise serializers.ValidationError({
                "error": (
                    f"Maximum active API keys limit ({max_allowed}) "
                    f"reached for your {user.profile.plan_type} plan."
                )
            })
        return attrs