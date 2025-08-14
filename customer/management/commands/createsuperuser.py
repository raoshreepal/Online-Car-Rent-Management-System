from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.core.exceptions import ValidationError
import getpass

User = get_user_model()

class Command(createsuperuser.Command):
    help = "Create a user with only username and password"

    def handle(self, *args, **options):
        # Set the required fields to be prompted during the user creation
        options['email'] = None  # Will be handled later in the admin
        options['role'] = None   # Will be handled later in the admin
        
        # Proceed with the user creation using the existing 'createsuperuser' logic
        super().handle(*args, **options)

    def add_arguments(self, parser):
        # Add necessary arguments for creating a user (similar to 'createsuperuser')
        super().add_arguments(parser)
        
        # Set defaults for non-required fields
        parser.add_argument(
            '--role',
            default=None,
            help='Leave the role empty, to be filled in the admin panel.',
        )
        parser.add_argument(
            '--email',
            default=None,
            help='Leave the email empty, to be filled in the admin panel.',
        )
