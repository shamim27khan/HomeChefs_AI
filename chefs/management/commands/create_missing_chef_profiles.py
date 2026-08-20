from django.core.management.base import BaseCommand
from authentication.models import User
from chefs.models import ChefProfile

class Command(BaseCommand):
    help = 'Create missing ChefProfile for all chef users'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Only check for missing profiles, don\'t create them'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Create profile for specific user ID'
        )
    
    def handle(self, *args, **options):
        if options['user_id']:
            self.create_profile_for_user(options['user_id'])
        elif options['check']:
            self.check_missing_profiles()
        else:
            self.create_all_missing_profiles()
    
    def check_missing_profiles(self):
        """Check for chef users without profiles"""
        chef_users = User.objects.filter(role='chef')
        missing_profiles = []
        
        for chef in chef_users:
            try:
                profile = chef.chefprofile
            except ChefProfile.DoesNotExist:
                missing_profiles.append(chef)
        
        if missing_profiles:
            self.stdout.write(f'Found {len(missing_profiles)} chef users without profiles:')
            for chef in missing_profiles:
                self.stdout.write(f'  - {chef.username} (ID: {chef.id})')
        else:
            self.stdout.write('All chef users have profiles.')
    
    def create_profile_for_user(self, user_id):
        """Create profile for specific user"""
        try:
            user = User.objects.get(id=user_id)
            if user.role != 'chef':
                self.stdout.write(f'User {user.username} is not a chef')
                return
            
            try:
                profile = user.chefprofile
                self.stdout.write(f'Chef {user.username} already has a profile')
                return
            except ChefProfile.DoesNotExist:
                # Create profile with default values
                profile = ChefProfile.objects.create(
                    user=user,
                    phone_number=f"TEMP{user.id}{user.id}",
                    address_line1="Address to be updated",
                    area="Not set",
                    city="Not set", 
                    pincode="000000"
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created profile for chef {user.username}')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with ID {user_id} not found')
            )
    
    def create_all_missing_profiles(self):
        """Create profiles for all chef users without them"""
        chef_users = User.objects.filter(role='chef')
        created_count = 0
        
        for chef in chef_users:
            try:
                profile = chef.chefprofile
            except ChefProfile.DoesNotExist:
                # Create profile with default values
                profile = ChefProfile.objects.create(
                    user=chef,
                    phone_number=f"TEMP{chef.id}{chef.id}",
                    address_line1="Address to be updated",
                    area="Not set",
                    city="Not set", 
                    pincode="000000"
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created profile for chef {chef.username}')
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} chef profiles')
            )
        else:
            self.stdout.write('No missing chef profiles found.')
