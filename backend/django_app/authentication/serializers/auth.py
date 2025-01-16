from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.db import transaction
from .base import TimestampedSerializer
from django.contrib.auth import authenticate
from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from .profile import UserProfileSerializer
from datetime import timedelta
from ..models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text='Secure password'
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Must match password'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'phone_number',
            'organization',
            
        )
        extra_kwargs = {
            'email': {
                'required': True,
                'help_text': 'Valid email address'
            },
            'first_name': {
                'required': True,
                'help_text': 'User\'s first name'
            },
            'last_name': {
                'required': True,
                'help_text': 'User\'s last name'
            },
            'phone_number': {
                'required': False,
                'help_text': 'Optional phone number'
            },
            'organization': {
                'required': False,
                'help_text': 'Optional organization name'
            }
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        attrs.pop('confirm_password', None)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate credentials and return tokens with user data"""
        # Change authentication field from username to email
        authenticate_kwargs = {
            'email': attrs['email'],
            'password': attrs['password']
        }

        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        # Attempt authentication
        self.user = authenticate(**authenticate_kwargs)

        if not self.user:
            raise serializers.ValidationError({
                'detail': 'No active account found with the given credentials'
            })

        # Get token data
        data = super().validate(attrs)
        
        # Get request from context for client info
        request = self.context.get('request')
        client_info = self.get_client_info(request) if request else {}

        # Update response data with user info and session info
        data.update({
            'user': UserSerializer(self.user).data,
            'session_info': client_info
        })
        
        return data
    
    def get_client_info(self, request):
        """Get client session information"""
        return {
            'ip_address': request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] 
                        or request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'device_type': self.get_device_type(request),
            'location': self._get_location_from_ip(request)
        }

    def _get_location_from_ip(self, request):
        # Implement IP geolocation logic here
        return 'Unknown'

    def get_device_type(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent:
            return 'tablet'
        return 'desktop'

class UserSerializer(TimestampedSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    profile = UserProfileSerializer(read_only=True)
    workspaces = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'id', 
            'email',
            'password', 
            'confirm_password',
            'first_name', 
            'last_name', 
            'phone_number', 
            'organization',
            'is_verified', 
            'created_at',
            'updated_at',
            'last_login',
            'profile',
            'profile_picture',
            'workspaces'
        )
        read_only_fields = ('id', 'is_verified', 'created_at', 'updated_at', 'profile', 'workspaces')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': False},
            'organization': {'required': False},
        }
    
    def get_workspaces(self, obj):
        """Get all workspaces user belongs to with their role"""
        memberships = obj.workspace_memberships.select_related('workspace').all()
        return [{
            'id': membership.workspace.id,
            'name': membership.workspace.name,
            'role': membership.role,
            'is_owner': membership.workspace.owner_id == obj.id
        } for membership in memberships]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
            
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({
                "email": "User with this email already exists."
            })
            
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            **validated_data,
            password=password
        )
        
        # Create associated profile with default settings
        profile_data = {
            'plan_type': 'free',
            'notification_preferences': {
                'email_notifications': True,
                'workflow_notifications': True
            },
            'timezone': 'UTC',
            'usage_stats': {}
        }
        
        user.profile.objects.create(user=user, **profile_data)
        return user
    
class UserUpdateSerializer(TimestampedSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'email',
            'first_name', 
            'last_name', 
            'phone_number', 
            'organization',
            'is_verified', 
            'created_at',
            'updated_at',
            'profile',
            'profile_picture'
        )
        read_only_fields = ('id', 'is_verified', 'created_at', 'updated_at', 'profile')
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'organization': {'required': False},
        }

    def validate_email(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.email != value:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("User with this email already exists.")
        return value

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError(
                "No active account found with the given email address."
            )
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, 
            help_text='Email verification token')
    
    def validate_token(self, value):
        """ verify the verification token and expiration"""
        if not value or len(value) <= 32:
            raise serializers.ValidationError(
                "Invalid verification token"
            )
        return value
    
class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True,
            help_text='Email address to resend verification to'
        )
    def validate_email(self, value):
        """
        Validate email exists and verification status
        """
        try:
            user = User.objects.get(email=value)
            
            # Checking if already verified
            if user.is_verified:
                raise serializers.ValidationError(
                    "User is already verified."
                )
            #Checking rate limiting for resend
            if hasattr(user, 'email_verfication_sent_at') and user.email_verfication_sent_at:
                cooldown_period = timedelta(minutes=5)
                time_elapsed = timezone.now() - user.email_verfication_sent_at
                
                if time_elapsed < cooldown_period:
                    minutes_remaining = int((cooldown_period - time_elapsed).total_seconds() / 60)
                    raise serializers.ValidationError(
                        f'Please wait {minutes_remaining} minutes before requesting another verification email'
                    )
        except User.DoesNotExist:
            # Don't reveal if email exists
            pass
            
        return value
    
    class Meta:
        fields = ('email',)
        
class EmailVerificationResponseSerializer(serializers.ModelSerializer):
    """Serializer for verification response data"""
    class Meta:
        model = User
        fields = ('id', 'email', 'is_verified')
        read_only_fields = fields

class VerificationStatusSerializer(serializers.ModelSerializer):
    """Serializer for checking verification status"""
    class Meta:
        model = User
        fields = ('email', 'is_verified')
        read_only_fields = fields
        
class SocialAuthResponseSerializer(serializers.Serializer):
    """Serializer for social authentication response"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    is_new_user = serializers.BooleanField()
    social_provider = serializers.CharField()
    plan_type = serializers.ChoiceField(choices=UserProfile.PLAN_CHOICES)
    account_status = serializers.CharField()
    onboarding_completed = serializers.BooleanField()