from rest_framework import generics, viewsets, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.decorators import api_view
from ..models.activity import SecurityLog, UserActivity
from ..models.profile import UserProfile
from ..models.workspace import Workspace, WorkspaceMembership
from rest_framework.views import APIView
from ..serializers.auth import (
    EmailTokenObtainPairSerializer, 
    UserSerializer,
    PasswordResetSerializer,
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
    EmailVerificationResponseSerializer,
    ResendVerificationSerializer,
    VerificationStatusSerializer
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_summary="User Registration",
        operation_description="Register a new user account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='Valid email address'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='password',
                    description='Secure password'
                ),
                'confirm_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='password',
                    description='Must match password'
                ),
                'first_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User\'s first name'
                ),
                'last_name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User\'s last name'
                ),
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Optional phone number'
                ),
                'organization': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Optional organization name'
                ),
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="User created successfully",
                schema=UserSerializer
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid input",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        'password': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        'non_field_errors': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                    }
                )
            )
        },
        tags=['Authentication']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            try:
                # Create user
                user = serializer.save()
                
                organization_name = request.data.get('organization') or f"{user.first_name}'s Workspace"
                workspace = Workspace.objects.create(
                    name=organization_name,
                    owner=user,
                    plan_type='free',
                    settings={
                        'default_timezone': user.profile.timezone,
                        'created_from': 'registration'
                    }
                )

                # Add user as workspace admin
                WorkspaceMembership.objects.create(
                    workspace=workspace,
                    user=user,
                    role='admin',
                    invited_by=user
                )
                # Generate and send verification email
                user.generate_verification_token()
                user.send_verification_email()
                
                # Log registration
                SecurityLog.objects.create(
                    user=user,
                    action='user_registered',
                    details={
                        'ip_address': request.META.get('REMOTE_ADDR'),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'registration_method': 'email',
                        'default_workspace_created': str(workspace.id)
                    }
                )
                
                user_data = UserSerializer(user).data
                user_data['default_workspace'] = {
                    'id': workspace.id,
                    'name': workspace.name,
                    'role': 'admin'
                }
                
                return Response(
                    user_data,
                    status=status.HTTP_201_CREATED
                )
                
            except Exception as e:
                return Response(
                    {
                        'error': 'Registration failed',
                        'detail': str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    throttle_classes = [AnonRateThrottle]
    
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Login with email and password to obtain JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        },
        tags=['Authentication']
    )

    def get_client_info(self, request):
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
    @api_view(['POST', 'OPTIONS'])
    def login_view(request):
        if request.method == 'OPTIONS':
            response = Response()
            response["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response["Access-Control-Allow-Credentials"] = "true"
            return response
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            # Log successful login
            SecurityLog.objects.create(
                user=user,
                action='login_success',
                details={
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )

            # Update user's last login
            user.last_login = datetime.now()
            user.save(update_fields=['last_login'])

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            # Get user if email is provided
            email = request.data.get('email')
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.get(email=email)
                # Log failed login attempt
                SecurityLog.objects.create(
                    user=user,
                    action='login_failed',
                    details={
                        'ip_address': request.META.get('REMOTE_ADDR'),
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'reason': str(e)
                    }
                )
            except User.DoesNotExist:
                pass

            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout user and blacklist refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                examples={
                    "application/json": {
                        "message": "Successfully logged out"
                    }
                }
            )
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Log logout
            SecurityLog.objects.create(
                user=request.user,
                action='logout',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response(
                {"message": "Successfully logged out"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class PasswordResetView(APIView):
    throttle_classes = [AnonRateThrottle]
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Send password reset email",
        request_body=PasswordResetSerializer,
        responses={
            200: openapi.Response(
                description="Password reset email sent",
                examples={
                    "application/json": {
                        "detail": "Password reset email sent if account exists"
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            email = serializer.validated_data['email']
            user = User.objects.get(email=email, is_active=True)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset URL
            reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'
            
            # Send email
            send_mail(
                subject='Password Reset Request',
                message=f'Click the following link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            SecurityLog.objects.create(
                user=user,
                action='password_reset_requested',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
        except User.DoesNotExist:
            # Don't reveal whether email exists
            pass
            
        return Response({
            'detail': 'Password reset email sent if account exists'
        })
        
class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Verify user's email address using verification token",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                schema=EmailVerificationResponseSerializer
            ),
            400: openapi.Response(
                description="Invalid token",
                examples={
                    "application/json": {
                        "detail": "Invalid or expired verification token"
                    }
                }
            ),
            429: "Too many verification attempts"
        }
    )
    def post(self, request):
        """Verify user's email address"""
        serializer = self.serializer_class(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data['token']
            
            # Find user by verification token
            try:
                user = User.objects.get(email_verification_token=token)
                
                # Check if token is not expired
                if user.is_verification_token_expired():
                    raise ValidationError('Verification token has expired')
                
                # Update user verification status
                user.is_verified = True
                user.email_verification_token = None
                user.email_verification_sent_at = None
                user.save()
                
                # Log verification success
                SecurityLog.objects.create(
                    user=user,
                    action='email_verified',
                    details={
                        'verification_method': 'token',
                        'email': user.email,
                        'ip_address': request.META.get('REMOTE_ADDR'),
                        'user_agent': request.META.get('HTTP_USER_AGENT', '')
                    }
                )
                response_serializer = EmailVerificationResponseSerializer(user)
                return Response(response_serializer.data)
                
            except User.DoesNotExist:
                # Log failed attempt
                SecurityLog.objects.create(
                    action='email_verification_failed',
                    details={
                        'reason': 'invalid_token',
                        'token': token,
                        'ip_address': request.META.get('REMOTE_ADDR')
                    }
                )
                raise ValidationError('Invalid verification token')
                
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'detail': 'An error occurred during verification'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Resend email verification token",
        request_body=ResendVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Verification email sent",
                examples={
                    "application/json": {
                        "detail": "Verification email sent successfully"
                    }
                }
            ),
            400: "Invalid email",
            429: "Too many resend attempts"
        }
    )
    def put(self, request):
        """Resend verification email"""
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_verified=False)
            
            # Check if we can send a new verification email
            # Generate and send new verification token
            user.generate_verification_token()
            user.send_verification_email()
            
            SecurityLog.objects.create(
                user=user,
                action='verification_email_resent',
                details={
                    'email': email,
                    'ip_address': request.META.get('REMOTE_ADDR')
                }
            )
                
            return Response({
                    'detail': 'Verification email sent successfully'
            })
                
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'detail': 'Verification email sent if account exists'
            })
            
        except Exception as e:
            return Response(
                {'detail': 'Failed to send verification email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @swagger_auto_schema(
        operation_description="Check email verification status",
        manual_parameters=[
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                description="Email address to check verification status",
                type=openapi.TYPE_STRING,
                format='email'
            )
        ],
        responses={
            200: VerificationStatusSerializer
        }
    )
    
    def get(self, request):
        """Check Verification Status of the email address"""
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {'detail': 'Email address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            serializer = VerificationStatusSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Email not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Confirm password reset with token and new password",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="Password reset successful",
                examples={
                    "application/json": {
                        "detail": "Password has been reset successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input",
                examples={
                    "application/json": {
                        "detail": "Invalid or expired reset token"
                    }
                }
            ),
            429: "Too many reset attempts"
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            # Extract user ID from the token
            try:
                uid = urlsafe_base64_decode(token.split('-')[0]).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                raise ValidationError('Invalid reset token')
                
            # Verify token
            if not default_token_generator.check_token(user, token.split('-')[1]):
                # Log failed attempt
                SecurityLog.objects.create(
                    user=user,
                    action='password_reset_failed',
                    details={
                        'reason': 'invalid_token',
                        'ip_address': request.META.get('REMOTE_ADDR')
                    }
                )
                raise ValidationError('Reset token has expired')
                
            # Set new password
            user.set_password(password)
            user.save()
            
            # Invalidate all existing sessions
            user.session_set.all().delete()
            
            # Log successful password reset
            SecurityLog.objects.create(
                user=user,
                action='password_reset_successful',
                details={
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
            
            return Response({
                'detail': 'Password has been reset successfully'
            })
            
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'detail': 'An error occurred during password reset'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )