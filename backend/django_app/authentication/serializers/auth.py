from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from .base import TimestampedSerializer
from django.contrib.auth import authenticate
from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from .profile import UserProfileSerializer

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

        # Add user data to response
        data['user'] = UserSerializer(self.user).data

        return data

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
            'profile'
        )
        read_only_fields = ('id', 'is_verified', 'created_at', 'updated_at', 'profile')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': False},
            'organization': {'required': False},
        }

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
    token = serializers.CharField(required=True)