from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    """
    Extended user profile with plan and preferences
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        primary_key=True  # Make this the primary key to prevent duplicate profiles
    )
    timezone = models.CharField(max_length=50, default='UTC')
    notification_preferences = models.JSONField(
        default=dict,
        help_text=_("User's notification settings")
    )
    api_key = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True, 
        null=True,
        help_text=_("API key for external access")
    )
    max_workflows = models.IntegerField(
        default=10,
        help_text=_("Maximum number of workflows allowed")
    )
    plan_type = models.CharField(
        max_length=20, 
        choices=PLAN_CHOICES, 
        default='free',
        help_text=_("User's subscription plan")
    )
    usage_stats = models.JSONField(
        default=dict,
        help_text=_("Usage statistics and metrics")
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f"{self.user.email}'s profile"

    def get_workflow_limit(self):
        """Get the workflow limit for user's current plan"""
        from django.conf import settings
        return settings.WORKFLOW_LIMITS.get(
            self.plan_type,
            settings.DEFAULT_WORKFLOW_LIMIT
        )

    def has_reached_workflow_limit(self):
        """Check if user has reached their workflow limit"""
        current_count = self.user.workflow_set.filter(is_active=True).count()
        return current_count >= self.get_workflow_limit()

    def workflows_remaining(self):
        """Get number of workflows remaining"""
        current_count = self.user.workflow_set.filter(is_active=True).count()
        return max(0, self.get_workflow_limit() - current_count)

class Team(models.Model):
    """
    Team model for group collaboration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_teams'
    )
    members = models.ManyToManyField(
        User, 
        related_name='teams', 
        through='TeamMembership'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    def __str__(self):
        return self.name

class TeamMembership(models.Model):
    """
    Team membership with role-based access
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(  # Changed from 'users' to 'user'
        User, 
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='viewer'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'team')  # Changed from 'users' to 'user'
        verbose_name = _('team membership')
        verbose_name_plural = _('team memberships')

    def __str__(self):
        return f"{self.user.email} - {self.team.name} ({self.role})"

class APIKey(models.Model):
    """
    API Keys for external integrations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='api_keys'
    )
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('API key')
        verbose_name_plural = _('API keys')

    def __str__(self):
        return f"{self.name} - {self.user.email}"

class LoginHistory(models.Model):
    """
    Track user login history
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_history'
    )
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default='success')

    class Meta:
        ordering = ['-login_time']
        verbose_name = _('login history')
        verbose_name_plural = _('login histories')

    def __str__(self):
        return f"{self.user.email} - {self.login_time}"
    
    
class TeamActivity(models.Model):
    """Track team activities"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

class TeamAuditLog(models.Model):
    """Audit log for team changes"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
class UserActivity(models.Model):
    """Track user activities"""
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']