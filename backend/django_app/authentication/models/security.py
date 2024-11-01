from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .base import BaseModel
from datetime import timezone
import secrets

def generate_api_key():
    return secrets.token_urlsafe(32)

class APIKey(BaseModel):
    user = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='api_keys'
    )
    name = models.CharField(max_length=100)
    key = models.CharField(
        max_length=100, 
        unique=True,
        default=generate_api_key
    )
    scopes = models.JSONField(
        default=list,
        help_text=_("List of allowed scopes for this API key")
    )
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    rate_limit = models.PositiveIntegerField(
        default=100,
        help_text=_("Maximum requests per hour")
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('API key')
        verbose_name_plural = _('API keys')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['key']),
        ]

    def clean(self):
        if self.expires_at and self.expires_at < timezone.now():
            raise ValidationError(_("Expiration date cannot be in the past"))

    def has_scope(self, scope):
        return scope in self.scopes

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
class LoginHistory(BaseModel):
    """Track user login attempts and details"""
    LOGIN_STATUS_CHOICES = [
        ('success', _('Success')),
        ('failed', _('Failed')),
        ('blocked', _('Blocked')),
        ('suspicious', _('Suspicious')),
    ]

    user = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='login_history'
    )
    status = models.CharField(
        max_length=20, 
        choices=LOGIN_STATUS_CHOICES,
        default='success'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("IP address of the login attempt")
    )
    user_agent = models.TextField(
        blank=True,
        help_text=_("Browser/client user agent")
    )
    location = models.CharField(
        max_length=255, 
        blank=True,
        help_text=_("Geographic location based on IP")
    )
    device_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Type of device used for login")
    )
    login_time = models.DateTimeField(auto_now_add=True)
    login_method = models.CharField(
        max_length=20,
        default='email',
        choices=[
            ('email', _('Email')),
            ('google', _('Google')),
            ('github', _('GitHub')),
            ('api', _('API')),
        ],
        help_text=_("Method used for authentication")
    )
    failure_reason = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Reason for login failure if status is 'failed'")
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('login history')
        verbose_name_plural = _('login histories')
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.status} - {self.created_at}"

    @classmethod
    def log_login_attempt(cls, user, status, ip_address=None, user_agent=None, 
                         location=None, device_type=None, login_method='email', 
                         failure_reason=None):
        """
        Helper method to create a login history entry
        """
        return cls.objects.create(
            user=user,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            device_type=device_type,
            login_method=login_method,
            failure_reason=failure_reason
        )

    @classmethod
    def get_recent_failures(cls, user, minutes=30):
        """
        Get recent failed login attempts for a user
        """
        cutoff_time = timezone.now() - timezone.timedelta(minutes=minutes)
        return cls.objects.filter(
            user=user,
            status='failed',
            created_at__gte=cutoff_time
        ).count()

    @classmethod
    def is_ip_suspicious(cls, ip_address, timeframe_minutes=30, threshold=10):
        """
        Check if an IP address has too many failed attempts
        """
        if not ip_address:
            return False
            
        cutoff_time = timezone.now() - timezone.timedelta(minutes=timeframe_minutes)
        failed_attempts = cls.objects.filter(
            ip_address=ip_address,
            status='failed',
            created_at__gte=cutoff_time
        ).count()
        
        return failed_attempts >= threshold