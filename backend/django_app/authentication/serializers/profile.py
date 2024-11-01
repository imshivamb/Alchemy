# serializers/profile.py

from .base import TimestampedSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models import UserProfile 

User = get_user_model()

class UserProfileSerializer(TimestampedSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'timezone', 
            'notification_preferences', 
            'max_workflows', 
            'usage_stats', 
            'plan_type',
            'onboarding_completed',
            'account_status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'plan_type', 
            'max_workflows', 
            'usage_stats',
            'created_at',
            'updated_at'
        ]

    def validate_notification_preferences(self, value):
        """Validate notification preferences structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Notification preferences must be an object"
            )
        
        required_keys = {'email_notifications', 'workflow_notifications'}
        if not all(key in value for key in required_keys):
            raise serializers.ValidationError(
                f"Notification preferences must contain all required keys: {required_keys}"
            )
        
        return value

    def validate_timezone(self, value):
        """Validate timezone value"""
        try:
            from pytz import timezone as pytz_timezone
            pytz_timezone(value)
        except Exception:
            raise serializers.ValidationError(
                "Invalid timezone"
            )
        return value

class UserPlanUpdateSerializer(serializers.Serializer):
    PLAN_CHOICES = UserProfile.PLAN_CHOICES  # Get choices directly from model
    
    plan_type = serializers.ChoiceField(
        choices=PLAN_CHOICES,
        required=True,
        help_text="The plan type to update to"
    )
    
    def validate_plan_type(self, value):
        user = self.context['request'].user
        if value == user.profile.plan_type:
            raise serializers.ValidationError(
                "User is already on this plan."
            )
            
        # You might want to add additional validation here
        # For example, checking if the user is allowed to upgrade to this plan
        
        return value

class FullUserProfileSerializer(UserProfileSerializer):
    """Extended serializer for full user profile details"""
    user = serializers.SerializerMethodField()
    subscription_info = serializers.SerializerMethodField()
    
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ['user', 'subscription_info']
        
    def get_user(self, obj):
        """Get basic user information"""
        return {
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'is_verified': obj.user.is_verified
        }
        
    def get_subscription_info(self, obj):
        """Get subscription related information"""
        return {
            'plan_type': obj.plan_type,
            'max_workflows': obj.max_workflows,
            'workflows_used': obj.get_workflows_count(),
            'api_keys_used': obj.get_api_keys_count(),
            'account_status': obj.account_status
        }

    def update(self, instance, validated_data):
        """Custom update to handle nested updates"""
        notification_prefs = validated_data.pop('notification_preferences', None)
        if notification_prefs:
            current_prefs = instance.notification_preferences
            current_prefs.update(notification_prefs)
            instance.notification_preferences = current_prefs
            
        return super().update(instance, validated_data)