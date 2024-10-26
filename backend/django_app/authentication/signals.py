# authentication/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import TeamMembership, User, UserProfile
from django.db import transaction

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update UserProfile when a User is created/updated"""
    if created:
        # Only create profile if it doesn't exist
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'plan_type': 'free',
                'notification_preferences': {},
                'usage_stats': {}
            }
        )
    else:
        # Update existing profile
        if hasattr(instance, 'profile'):
            instance.profile.save()

@receiver(post_save, sender=TeamMembership)
def handle_team_membership(sender, instance, created, **kwargs):
    """Handle team membership changes"""
    if created:
        try:
            # Send email notification
            send_mail(
                subject=f'Added to team: {instance.team.name}',
                message=f'You have been added to the team {instance.team.name} as {instance.role}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )
            
            # Update user's team count in profile
            teams_count = instance.user.teams.count()
            if hasattr(instance.user, 'profile'):
                instance.user.profile.usage_stats.update({
                    'teams_count': teams_count,
                    'last_team_joined': instance.team.name
                })
                instance.user.profile.save()
        except Exception as e:
            print(f"Error in handle_team_membership: {str(e)}")

@receiver(post_delete, sender=TeamMembership)
def handle_team_membership_removal(sender, instance, **kwargs):
    """Handle team membership removal"""
    try:
        # Send notification
        send_mail(
            subject=f'Removed from team: {instance.team.name}',
            message=f'You have been removed from the team {instance.team.name}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=True,
        )
        
        # Update user's team count
        teams_count = instance.user.teams.count()
        if hasattr(instance.user, 'profile'):
            instance.user.profile.usage_stats.update({
                'teams_count': teams_count,
                'last_team_left': instance.team.name
            })
            instance.user.profile.save()
    except Exception as e:
        print(f"Error in handle_team_membership_removal: {str(e)}")