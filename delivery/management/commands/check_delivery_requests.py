from django.core.management.base import BaseCommand
from django.utils import timezone
from delivery.notifications import DeliveryNotificationSystem

class Command(BaseCommand):
    help = 'Check expired delivery requests and auto-reassign orders if needed'
    
    def handle(self, *args, **options):
        self.stdout.write('Checking expired delivery requests...')
        
        # Check expired requests
        expired_count = DeliveryNotificationSystem.check_expired_requests()
        self.stdout.write(f'Marked {expired_count} requests as expired')
        
        # Auto-reassign orders if needed
        # This would typically be run as a cron job every few minutes
        # For now, we'll just log that the check was completed
        
        self.stdout.write(self.style.SUCCESS('Delivery request check completed'))
