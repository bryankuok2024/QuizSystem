import hashlib
import json
from django.core.management.base import BaseCommand
from django.db.models import Q
from questions.models import Question

class Command(BaseCommand):
    help = 'Finds all questions with a NULL or empty question_hash and generates a new one.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting to backfill question hashes...'))
        
        questions_to_update = Question.objects.filter(
            Q(question_hash__isnull=True) | Q(question_hash='')
        )
        
        count = 0
        total = questions_to_update.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS('No questions needed updating. All hashes are already present.'))
            return

        self.stdout.write(f'Found {total} questions to update.')

        for question in questions_to_update:
            try:
                options_string = json.dumps(question.options, sort_keys=True) if question.options else ""
                hash_string = f"{question.content}-{options_string}".encode('utf-8')
                new_hash = hashlib.sha256(hash_string).hexdigest()
                
                question.question_hash = new_hash
                question.save()
                
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Successfully updated hash for question ID: {question.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Could not update question ID: {question.id}. Error: {e}'))

        self.stdout.write(self.style.NOTICE(f'Finished. Successfully updated {count}/{total} questions.')) 