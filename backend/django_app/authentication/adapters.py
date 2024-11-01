from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.github.provider import GitHubProvider
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.utils import timezone
from . import models

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """Save user from social login"""
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data
        provider = sociallogin.account.provider
        
        try:
            # Update user info based on provider
            if provider == 'google':
                user.email = data.get('email', '')
                user.first_name = data.get('given_name', '')
                user.last_name = data.get('family_name', '')
                user.profile_picture = data.get('picture', '')
            
            elif provider == 'github':
                user.email = data.get('email', '')
                name_parts = data.get('name', '').split(' ', 1)
                user.first_name = name_parts[0] if name_parts else ''
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                user.profile_picture = data.get('avatar_url', '')
            
            user.is_verified = True
            user.save()

            # Create or update profile
            profile, created = models.UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'plan_type': 'free',
                    'notification_preferences': {
                        'email_notifications': True,
                        'workflow_notifications': True
                    },
                    'timezone': 'UTC',
                    'usage_stats': {
                        'created_at': timezone.now().isoformat(),
                        'login_provider': provider
                    }
                }
            )

            # Log social authentication
            models.SecurityLog.objects.create(
                user=user,
                action=f'{provider}_auth',
                details={
                    'provider': provider,
                    'email_verified': user.is_verified
                }
            )

        except Exception as e:
            print(f"Error in social account adapter: {str(e)}")
            # Add proper logging here

        return user