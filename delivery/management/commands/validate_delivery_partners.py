from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from delivery.models import DeliveryPartner

class Command(BaseCommand):
    help = 'Validate and manage delivery partners'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all delivery partners'
        )
        parser.add_argument(
            '--pending',
            action='store_true',
            help='List pending partners'
        )
        parser.add_argument(
            '--verify',
            type=int,
            help='Verify partner by ID'
        )
        parser.add_argument(
            '--reject',
            type=int,
            help='Reject partner by ID'
        )
        parser.add_argument(
            '--activate',
            type=int,
            help='Activate partner by ID'
        )
        parser.add_argument(
            '--deactivate',
            type=int,
            help='Deactivate partner by ID'
        )
    
    def handle(self, *args, **options):
        if options['list']:
            self.list_partners()
        elif options['pending']:
            self.list_pending()
        elif options['verify']:
            self.verify_partner(options['verify'])
        elif options['reject']:
            self.reject_partner(options['reject'])
        elif options['activate']:
            self.activate_partner(options['activate'])
        elif options['deactivate']:
            self.deactivate_partner(options['deactivate'])
        else:
            self.show_help()
    
    def list_partners(self):
        """List all delivery partners"""
        partners = DeliveryPartner.objects.all().select_related('user')
        
        if not partners.exists():
            self.stdout.write('No delivery partners found')
            return
        
        self.stdout.write('All Delivery Partners:')
        self.stdout.write('=' * 80)
        
        for partner in partners:
            self.stdout.write(
                f"ID: {partner.id} | "
                f"User: {partner.user.username} | "
                f"Phone: {partner.phone_number} | "
                f"Status: {partner.get_status_display()} | "
                f"Verification: {partner.get_verification_status_display()} | "
                f"Available: {partner.is_available}"
            )
    
    def list_pending(self):
        """List pending partners"""
        pending = DeliveryPartner.objects.filter(
            verification_status='pending'
        ).select_related('user')
        
        if not pending.exists():
            self.stdout.write('No pending partners found')
            return
        
        self.stdout.write('Pending Delivery Partners:')
        self.stdout.write('=' * 80)
        
        for partner in pending:
            self.stdout.write(
                f"ID: {partner.id} | "
                f"User: {partner.user.username} | "
                f"Email: {partner.user.email} | "
                f"Phone: {partner.phone_number} | "
                f"Vehicle: {partner.get_vehicle_type_display()} | "
                f"Areas: {partner.service_areas}"
            )
    
    def verify_partner(self, partner_id):
        """Verify a delivery partner"""
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
            
            partner.verification_status = 'verified'
            partner.status = 'active'
            partner.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Partner {partner.user.username} (ID: {partner_id}) verified and activated'
                )
            )
            
        except DeliveryPartner.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'✗ Partner with ID {partner_id} not found')
            )
    
    def reject_partner(self, partner_id):
        """Reject a delivery partner"""
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
            
            partner.verification_status = 'rejected'
            partner.status = 'inactive'
            partner.is_available = False
            partner.save()
            
            self.stdout.write(
                self.style.WARNING(
                    f'✗ Partner {partner.user.username} (ID: {partner_id}) rejected'
                )
            )
            
        except DeliveryPartner.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'✗ Partner with ID {partner_id} not found')
            )
    
    def activate_partner(self, partner_id):
        """Activate a delivery partner"""
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
            
            partner.status = 'active'
            partner.is_available = True
            partner.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Partner {partner.user.username} (ID: {partner_id}) activated'
                )
            )
            
        except DeliveryPartner.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'✗ Partner with ID {partner_id} not found')
            )
    
    def deactivate_partner(self, partner_id):
        """Deactivate a delivery partner"""
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
            
            partner.status = 'inactive'
            partner.is_available = False
            partner.save()
            
            self.stdout.write(
                self.style.WARNING(
                    f'✗ Partner {partner.user.username} (ID: {partner_id}) deactivated'
                )
            )
            
        except DeliveryPartner.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'✗ Partner with ID {partner_id} not found')
            )
    
    def show_help(self):
        """Show help information"""
        self.stdout.write('Delivery Partner Management Commands:')
        self.stdout.write('--list          List all delivery partners')
        self.stdout.write('--pending       List pending partners')
        self.stdout.write('--verify ID     Verify partner by ID')
        self.stdout.write('--reject ID     Reject partner by ID')
        self.stdout.write('--activate ID   Activate partner by ID')
        self.stdout.write('--deactivate ID Deactivate partner by ID')
        
        # Show examples
        self.stdout.write('\nExamples:')
        self.stdout.write('python manage.py validate_delivery_partners --pending')
        self.stdout.write('python manage.py validate_delivery_partners --verify 1')
        self.stdout.write('python manage.py validate_delivery_partners --activate 1')
