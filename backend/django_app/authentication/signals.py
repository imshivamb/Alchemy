from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from .models import TeamMembership, User, UserProfile, SecurityLog
from django.db import transaction

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update UserProfile when a User is created/updated"""
    try:
        with transaction.atomic():
            if created:
                UserProfile.objects.create(
            user=instance,
            plan_type='free',
            notification_preferences={
                'email_notifications': True,
                'workflow_notifications': True
            },
            timezone='UTC',
            usage_stats={
                'registration_date': datetime.now().isoformat(),
                'last_login': None
            },
            max_workflows=3
        )
                
                # Log user creation
                SecurityLog.objects.create(
                    user=instance,
                    action='user_created',
                    details={
                        'registration_method': 'email' if instance.password else 'social'
                    }
                )
            else:
                UserProfile.objects.filter(user=instance).update(
                updated_at=timezone.now()
        )
    except Exception as e:
        print(f"Error in create_or_update_user_profile: {str(e)}")
        # You might want to add proper logging here

@receiver(post_save, sender=TeamMembership)
def handle_team_membership(sender, instance, created, **kwargs):
    """Handle team membership changes"""
    try:
        with transaction.atomic():
            if created:
                # Send email notification
                send_mail(
                    subject=f'Added to team: {instance.team.name}',
                    message=f'You have been added to the team {instance.team.name} as {instance.role}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.user.email],
                    fail_silently=True,
                )
                
                # Update user's profile stats
                if hasattr(instance.user, 'profile'):
                    instance.user.profile.usage_stats.update({
                        'teams_count': instance.user.teams.count(),
                        'last_team_joined': {
                            'name': instance.team.name,
                            'role': instance.role,
                            'date': timezone.now().isoformat()
                        }
                    })
                    instance.user.profile.save()
                
                # Log membership creation
                SecurityLog.objects.create(
                    user=instance.user,
                    action='team_joined',
                    details={
                        'team_id': str(instance.team.id),
                        'team_name': instance.team.name,
                        'role': instance.role
                    }
                )
    except Exception as e:
        print(f"Error in handle_team_membership: {str(e)}")

@receiver(post_delete, sender=TeamMembership)
def handle_team_membership_removal(sender, instance, **kwargs):
    """Handle team membership removal"""
    try:
        with transaction.atomic():
            # Send notification
            send_mail(
                subject=f'Removed from team: {instance.team.name}',
                message=f'You have been removed from the team {instance.team.name}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )
            
            # Update user's profile stats
            if hasattr(instance.user, 'profile'):
                instance.user.profile.usage_stats.update({
                    'teams_count': instance.user.teams.count(),
                    'last_team_left': {
                        'name': instance.team.name,
                        'date': timezone.now().isoformat()
                    }
                })
                instance.user.profile.save()
            
            # Log membership removal
            SecurityLog.objects.create(
                user=instance.user,
                action='team_left',
                details={
                    'team_id': str(instance.team.id),
                    'team_name': instance.team.name,
                    'role': instance.role
                }
            )
    except Exception as e:
        print(f"Error in handle_team_membership_removal: {str(e)}")