from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test email configuration'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("Testing email configuration...")
            
            send_mail(
                subject='Test Email',
                message='This is a test email from your Django application.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('Test email sent successfully! Check your console output.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {str(e)}'))