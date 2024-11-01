from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from .base import BaseModel

class UserProfile(BaseModel):
    PLAN_CHOICES = [
        ('free', _('Free')),
        ('basic', _('Basic')),
        ('premium', _('Premium')),
        ('enterprise', _('Enterprise')),
    ]
    
    def default_preferences():
        return {
        'email_notifications': True,
        'workflow_notifications': True,
        'timezone': 'UTC',
        'language': 'en'
    }
    
    user = models.OneToOneField(
        'User', 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    plan_type = models.CharField(
        max_length=20, 
        choices=PLAN_CHOICES, 
        default='free'
    )
    notification_preferences = models.JSONField(
        default=default_preferences,
        help_text=_("User's notification settings")
    )
    max_workflows = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text=_("Maximum number of workflows allowed")
    )
    usage_stats = models.JSONField(
        default=dict,
        help_text=_("Usage statistics and metrics")
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text=_("User's timezone")
    )
    onboarding_completed = models.BooleanField(default=False)
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', _('Active')),
            ('suspended', _('Suspended')),
            ('cancelled', _('Cancelled'))
        ],
        default='active'
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        indexes = [
            models.Index(fields=['plan_type', 'account_status']),
        ]

    def __str__(self):
        return f"{self.user.email}'s profile"

    @property
    def is_paid_plan(self):
        return self.plan_type != 'free'

    def update_usage_stats(self, metric, value):
        if not self.usage_stats.get('metrics'):
            self.usage_stats['metrics'] = {}
        self.usage_stats['metrics'][metric] = value
        self.save()
        
    def get_workflows_count(self):
        """Get count of active workflows"""
        return self.user.workflow_set.filter(is_active=True).count()
    
    def get_api_keys_count(self):
        """Get count of active API keys"""
        return self.user.api_keys.filter(is_active=True).count()
    
    def get_api_key_limit(self):
        """Get API key limit based on plan"""
        from django.conf import settings
        return settings.API_KEY_LIMITS.get(
            self.plan_type, 
            settings.DEFAULT_API_KEY_LIMIT
        )
    
    def has_reached_workflow_limit(self):
        """Check if user has reached workflow limit"""
        from django.conf import settings
        limit = settings.WORKFLOW_LIMITS.get(
            self.plan_type,
            settings.DEFAULT_WORKFLOW_LIMIT
        )
        return self.get_workflows_count() >= limit