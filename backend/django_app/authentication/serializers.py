from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Team, TeamMembership, APIKey, UserActivity, TeamActivity, TeamAuditLog
from django.conf import settings
from django.db import transaction
from django.db.models import Count

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model
    Used for nested profile data within UserSerializer
    """
    class Meta:
        model = UserProfile
        fields = ['timezone', 'notification_preferences', 'max_workflows', 'usage_stats', 'api_key']
        read_only_fields = ['api_key']
        
    extra_kwargs = {
            'timezone': {'required': False},
            'notification_preferences': {'required': False},
            'max_workflows': {'required': False},
            'usage_stats': {'required': False},
        }
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True) 
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'confirm_password', 'email',
            'first_name', 'last_name', 'phone_number', 'organization',
            'is_verified', 'created_at'
        )
        read_only_fields = ('id', 'is_verified', 'created_at')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'organization': {'required': False},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        # Remove confirm_password from the data
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        # Create user instance
        user = User.objects.create_user(
            **validated_data,
            password=password
        )
        
        # Create profile if it doesn't exist
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'plan_type': 'free',
                'notification_preferences': {},
                'usage_stats': {}
            }
        )
        
        return user

class TeamSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    members_count = serializers.SerializerMethodField() 
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'owner', 'members', 'members_count', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        return obj.members.count()

class TeamMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'username', 'team', 'role', 'joined_at']
        read_only_fields = ['joined_at']
    
    def validate(self, attrs):
        # Ensure user isn't already a member of the team
        if TeamMembership.objects.filter(user=attrs['user'], team=attrs['team']).exists():
            raise serializers.ValidationError({"user": "User is already a member of this team."})
        return attrs

class APIKeySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = APIKey
        fields = ['id', 'user', 'name', 'key', 'is_active', 'created_at', 'expires_at']
        read_only_fields = ['key', 'created_at']
    
    def validate(self, attrs):
        user = self.context['request'].user
        current_active_keys = user.api_keys.filter(is_active=True).count()
        
        # Get user's plan limit or default
        max_allowed = settings.API_KEY_LIMITS.get(
            user.profile.plan_type, 
            settings.DEFAULT_API_KEY_LIMIT
        )
        
        if current_active_keys >= max_allowed:
            raise serializers.ValidationError({
                "error": f"Maximum active API keys limit ({max_allowed}) reached for your {user.profile.plan_type} plan."
            })
        return attrs
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    
class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activities
    """
    class Meta:
        model = UserActivity
        fields = [
            'id',
            'action',
            'details',
            'ip_address',
            'user_agent',
            'timestamp'
        ]

class UserExportSerializer(serializers.ModelSerializer):
    """
    Serializer for exporting user data
    Includes detailed user information
    """
    teams = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    activity_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'organization',
            'is_active',
            'date_joined',
            'last_login',
            'teams',
            'profile',
            'activity_summary'
        ]
        
    def get_teams(self, obj):
        return TeamMembership.objects.filter(user=obj).values(
            'team__name',
            'role',
            'joined_at'
        )
        
    def get_profile(self, obj):
        return {
            'plan_type': obj.profile.plan_type,
            'max_workflows': obj.profile.max_workflows,
            'timezone': obj.profile.timezone
        }
        
    def get_activity_summary(self, obj):
        recent_activities = UserActivity.objects.filter(
            user=obj
        ).order_by('-timestamp')[:5]
        return UserActivitySerializer(recent_activities, many=True).data

class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for team activities
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamActivity
        fields = [
            'id',
            'team',
            'user',
            'action',
            'details',
            'timestamp'
        ]
        
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'name': f"{obj.user.first_name} {obj.user.last_name}".strip()
        } if obj.user else None

class TeamAuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for team audit logs
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamAuditLog
        fields = [
            'id',
            'team',
            'user',
            'action',
            'changes',
            'timestamp'
        ]
        
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'name': f"{obj.user.first_name} {obj.user.last_name}".strip()
        } if obj.user else None

class TeamMembershipDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for team membership
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMembership
        fields = [
            'id',
            'user',
            'role',
            'joined_at'
        ]
        
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'name': f"{obj.user.first_name} {obj.user.last_name}".strip(),
            'is_active': obj.user.is_active
        }

class DetailedTeamSerializer(serializers.ModelSerializer):
    """
    Detailed team serializer for admin views
    """
    members = TeamMembershipDetailSerializer(
        source='memberships',
        many=True,
        read_only=True
    )
    owner = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'description',
            'owner',
            'members',
            'created_at',
            'updated_at',
            'statistics'
        ]
        
    def get_owner(self, obj):
        return {
            'id': obj.owner.id,
            'email': obj.owner.email,
            'name': f"{obj.owner.first_name} {obj.owner.last_name}".strip()
        }
        
    def get_statistics(self, obj):
        return {
            'total_members': obj.members.count(),
            'active_members': obj.members.filter(is_active=True).count(),
            'roles': TeamMembership.objects.filter(team=obj).values(
                'role'
            ).annotate(count=Count('id'))
        }
        
class UserPlanUpdateSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(
        choices=['free', 'basic', 'premium', 'enterprise'],
        required=True,
        help_text="The plan type to update to"
    )