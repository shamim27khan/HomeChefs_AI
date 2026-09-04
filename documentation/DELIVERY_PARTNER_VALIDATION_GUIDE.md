from django.core.management.base import BaseCommand
from delivery.models import DeliveryPartner

class Command(BaseCommand):
    help = 'Validate pending delivery partners'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--partner-id',
            type=int,
            help='Specific partner ID to validate'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Validate all pending partners'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all pending partners'
        )
    
    def handle(self, *args, **options):
        if options['list']:
            self.list_pending_partners()
        elif options['partner_id']:
            self.validate_partner(options['partner_id'])
        elif options['all']:
            self.validate_all_pending()
        else:
            self.stdout.write('Use --list, --partner-id, or --all option')
    
    def list_pending_partners(self):
        """List all pending partners"""
        pending_partners = DeliveryPartner.objects.filter(verification_status='pending')
        
        if not pending_partners.exists():
            self.stdout.write('No pending partners found')
            return
        
        self.stdout.write('Pending Delivery Partners:')
        self.stdout.write('-' * 50)
        
        for partner in pending_partners:
            self.stdout.write(
                f"ID: {partner.id} | "
                f"User: {partner.user.username} | "
                f"Phone: {partner.phone_number} | "
                f"Vehicle: {partner.vehicle_type} ({partner.vehicle_number}) | "
                f"Areas: {partner.service_areas}"
            )
    
    def validate_partner(self, partner_id):
        """Validate a specific partner"""
        try:
            partner = DeliveryPartner.objects.get(id=partner_id)
            
            if partner.verification_status == 'verified':
                self.stdout.write(f'Partner {partner_id} is already verified')
                return
            
            partner.verification_status = 'verified'
            partner.status = 'active'
            partner.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Partner {partner.user.username} (ID: {partner_id}) validated successfully')
            )
            
        except DeliveryPartner.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Partner with ID {partner_id} not found')
            )
    
    def validate_all_pending(self):
        """Validate all pending partners"""
        pending_partners = DeliveryPartner.objects.filter(verification_status='pending')
        
        if not pending_partners.exists():
            self.stdout.write('No pending partners to validate')
            return
        
        count = pending_partners.count()
        pending_partners.update(verification_status='verified', status='active')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully validated {count} delivery partners')
        )
