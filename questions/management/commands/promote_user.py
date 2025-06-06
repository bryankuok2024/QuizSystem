from django.core.management.base import BaseCommand, CommandError
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Promotes a user to be a staff and superuser.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email of the user to promote.')

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise CommandError(f'User with email "{email}" does not exist.')

        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully promoted user "{email}" to superuser.')) 