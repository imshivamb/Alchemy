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
        
class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    timezone = models.CharField(max_length=50, default='UTC')
    notification_preferences = models.JSONField(default=dict)
    api_key = models.CharField(max_length=100, unique=True, blank=True, null=True)
    max_workflows = models.IntegerField(default=10)
    plan_type = models.CharField(
        max_length=20, 
        choices=PLAN_CHOICES, 
        default='free'
    )
    usage_stats = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
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
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    members = models.ManyToManyField(User, related_name='teams', through='TeamMembership')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('users', 'team')
        
class APIKey(models.Model):
    """
    API Keys for external integrations
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
class LoginHistory(models.Model):
    """
    Track user login history
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default='success')

    class Meta:
        ordering = ['-login_time']
    