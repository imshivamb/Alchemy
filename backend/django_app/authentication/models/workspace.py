from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import BaseModel

class Workspace(BaseModel):
    name = models.CharField(
        max_length=100,
        help_text=_("Workspace name")
    )
    owner = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE, 
        related_name='owned_workspaces'
    )
    plan_type = models.CharField(
        max_length=50,
        choices=[
            ('free', 'Free'),
            ('business', 'Business'),
            ('enterprise', 'Enterprise')
        ],
        default='free'
    )
    settings = models.JSONField(
        default=dict,
        help_text=_("Workspace settings and configurations")
    )
    members = models.ManyToManyField(
        'authentication.User',
        through='WorkspaceMembership',
        through_fields=('workspace', 'user'),
        related_name='workspaces'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('workspace')
        verbose_name_plural = _('workspaces')

class WorkspaceMembership(BaseModel):
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('member', _('Member')),
    ]
    
    workspace = models.ForeignKey(
        Workspace, 
        on_delete=models.CASCADE,
        related_name='workspace_members'
    )
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='workspace_memberships'
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='member'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='workspace_invites_sent'
    )

    class Meta:
        unique_together = ('user', 'workspace')
        verbose_name = _('workspace membership')
        verbose_name_plural = _('workspace memberships')
        indexes = [
            models.Index(fields=['user', 'workspace', 'role']),
        ]