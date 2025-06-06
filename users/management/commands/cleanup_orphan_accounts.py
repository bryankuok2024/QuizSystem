from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Finds and deletes orphan SocialAccount records that are not linked to any user.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting cleanup of orphan social accounts...'))
        
        # A more robust way to find orphans, especially if the user field itself is problematic
        all_accounts = SocialAccount.objects.all()
        orphan_ids = []
        for account in all_accounts:
            try:
                # Accessing the user will fail if it does not exist
                _ = account.user
            except ObjectDoesNotExist:
                orphan_ids.append(account.id)
                self.stdout.write(f'Found orphan account with ID: {account.id}, UID: {account.uid}, Provider: {account.provider}')
        
        if not orphan_ids:
            self.stdout.write(self.style.SUCCESS('No orphan social accounts found. Database is clean.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {len(orphan_ids)} orphan account(s). Deleting...'))
        
        # Perform the deletion
        queryset = SocialAccount.objects.filter(id__in=orphan_ids)
        delete_count, _ = queryset.delete()
        
        if delete_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {delete_count} orphan social account(s).'))
        else:
            self.stdout.write(self.style.ERROR('Deletion failed or no accounts were deleted in the final query.')) 