from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .base import BaseModel

class BaseActivity(BaseModel):
    ACTION_TYPES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('other', _('Other'))
    ]

    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_activities'
    )
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Generic foreign key for linking to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.UUIDField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

class UserActivity(BaseActivity):
    class Meta(BaseActivity.Meta):
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"

class TeamActivity(BaseActivity):
    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        related_name='activities'
    )

    class Meta(BaseActivity.Meta):
        verbose_name = _('team activity')
        verbose_name_plural = _('team activities')

    def __str__(self):
        return f"{self.team.name} - {self.action} by {self.user.email}"

class SecurityLog(BaseActivity):
    SEVERITY_LEVELS = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical'))
    ]

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='low'
    )
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)

    class Meta(BaseActivity.Meta):
        verbose_name = _('security log')
        verbose_name_plural = _('security logs')

    def __str__(self):
        return f"{self.severity} - {self.action} - {self.created_at}"