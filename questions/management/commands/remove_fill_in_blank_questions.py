from django.core.management.base import BaseCommand
from questions.models import Question
from django.db import transaction

class Command(BaseCommand):
    help = 'Removes all questions of the "fill_in_blank" type from the database.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Searching for 'fill_in_blank' questions to delete..."))
        
        questions_to_delete = Question.objects.filter(question_type='fill_in_blank')
        
        count = questions_to_delete.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No 'fill_in_blank' questions found. Nothing to delete."))
            return
            
        self.stdout.write(f"Found {count} 'fill_in_blank' question(s). Deleting them now...")
        
        questions_to_delete.delete()
        
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} question(s).")) 