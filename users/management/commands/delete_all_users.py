from django.core.management.base import BaseCommand
from users.models import User  # Use your custom user model

class Command(BaseCommand):
    help = 'Delete all users from the database'

    def handle(self, *args, **kwargs):
        User.objects.all().delete()  # Delete all users
        self.stdout.write(self.style.SUCCESS('Successfully deleted all users.'))
