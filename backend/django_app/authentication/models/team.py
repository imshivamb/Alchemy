from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .base import BaseModel

class Team(BaseModel):
    name = models.CharField(
        max_length=100,
        help_text=_("Team name")
    )
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='owned_teams'
    )
    members = models.ManyToManyField(
        'User', 
        related_name='teams', 
        through='TeamMembership',
        through_fields=('team', 'user')
        
    )
    max_members = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1)]
    )
    settings = models.JSONField(
        default=dict,
        help_text=_("Team settings and configurations")
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        indexes = [
            models.Index(fields=['owner', 'is_active']),
        ]

    def clean(self):
        if self.members.count() > self.max_members:
            raise ValidationError(_("Team has exceeded maximum member limit"))

    def add_member(self, user, role='viewer'):
        if self.members.count() >= self.max_members:
            raise ValidationError(_("Cannot add more members - team is at capacity"))
        return TeamMembership.objects.create(
            team=self,
            user=user,
            role=role
        )

class TeamMembership(BaseModel):
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('editor', _('Editor')),
        ('viewer', _('Viewer')),
    ]
    
    ROLE_PERMISSIONS = {
        'admin': ['manage_team', 'manage_members', 'manage_workflows', 'view_analytics'],
        'editor': ['edit_workflows', 'view_workflows', 'view_analytics'],
        'viewer': ['view_workflows']
    }
    
    user = models.ForeignKey(
        'User', 
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
    invited_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='team_invites_sent'
    )
    custom_permissions = models.JSONField(
        default=list,
        help_text=_("Additional custom permissions for this member")
    )

    class Meta:
        unique_together = ('user', 'team')
        verbose_name = _('team membership')
        verbose_name_plural = _('team memberships')
        indexes = [
            models.Index(fields=['user', 'team', 'role']),
        ]

    def has_permission(self, permission):
        base_permissions = self.ROLE_PERMISSIONS.get(self.role, [])
        return permission in base_permissions or permission in self.custom_permissions