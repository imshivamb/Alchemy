from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import validate_email, RegexValidator
from django.utils.translation import gettext_lazy as _
from .base import BaseModel
from .security import LoginHistory
from django.db import models
from django.core.mail import send_mail
from datetime import timezone
from datetime import timedelta
import secrets
from django.conf import settings

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        validate_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser, BaseModel):
    username = None
    # Required fields
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)

    # Optional fields
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )
    organization = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/%Y/%m/',
        null=True,
        blank=True
    )
    is_verified = models.BooleanField(
        _('email verified'),
        default=False
    )

    # Security and tracking fields
    failed_login_attempts = models.PositiveIntegerField(
        default=0
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True
    )
    email_verification_token = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    email_verification_sent_at = models.DateTimeField(
        null=True,
        blank=True
    )
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.email
    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError('Email is required')
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    def get_short_name(self):
        return self.first_name

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        self.save()

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.save()
        
    def log_login_success(self, ip_address=None, user_agent=None, location=None, 
                         device_type=None, login_method='email'):
        """Log successful login"""
        self.last_login = timezone.now()
        if hasattr(self, 'last_login_ip'):
            self.last_login_ip = ip_address
        self.failed_login_attempts = 0
        self.save()
        
        from .security import LoginHistory  # Import here to avoid circular imports
        return LoginHistory.objects.create(
            user=self,
            status='success',
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            device_type=device_type,
            login_method=login_method
        )

    def log_login_failure(self, ip_address=None, user_agent=None, location=None, 
                         device_type=None, login_method='email', failure_reason=None):
        """Log failed login attempt"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()  # Using Django's timezone
        self.save()
        
        from .security import LoginHistory  # Import here to avoid circular imports
        return LoginHistory.objects.create(
            user=self,
            status='failed',
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            device_type=device_type,
            login_method=login_method,
            failure_reason=failure_reason
        )

    def is_login_allowed(self):
        """Check if login is allowed based on failed attempts"""
        if self.failed_login_attempts >= 5:  # Can be moved to settings
            if self.last_failed_login:
                blocking_period = timezone.timedelta(minutes=30)  # Can be moved to settings
                if timezone.now() - self.last_failed_login < blocking_period:
                    return False
                # Reset counter if blocking period has passed
                self.failed_login_attempts = 0
                self.save()
        return True
    
    def generate_verification_token(self):
        """Generate a new verification token"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = timezone.now()
        self.save()
        
    def is_verification_token_expired(self):
        """Check if verification token has expired"""
        if not self.email_verification_sent_at:
            return True
            
        expiry_time = timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS)
        return timezone.now() > (self.email_verification_sent_at + expiry_time)
        
    def can_send_verification_email(self):
        """Check if we can send a new verification email"""
        if not self.email_verification_sent_at:
            return True
            
        cooldown = timedelta(minutes=settings.EMAIL_VERIFICATION_COOLDOWN_MINUTES)
        return timezone.now() > (self.email_verification_sent_at + cooldown)
        
    def send_verification_email(self):
        """Send verification email to user"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={self.email_verification_token}"
        
        send_mail(
            subject='Verify your email address',
            message=f'Click the following link to verify your email: {verification_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            fail_silently=False
        )