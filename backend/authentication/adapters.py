from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.github.provider import GitHubProvider
from allauth.socialaccount.providers.google.provider import GoogleProvider
from . import models

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data
        
        if isinstance(sociallogin.account.provider, GoogleProvider):
            # Handle Google data
            user.email = data.get('email', '')
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')
        
        elif isinstance(sociallogin.account.provider, GitHubProvider):
            # Handle GitHub data
            user.email = data.get('email', '')
            name_parts = data.get('name', '').split(' ', 1)
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            
        user.is_verified = True
        user.save()

        # Create or update profile
        profile, created = models.UserProfile.objects.get_or_create(user=user)
        if created:
            profile.plan_type = 'free'
            profile.save()

        return user