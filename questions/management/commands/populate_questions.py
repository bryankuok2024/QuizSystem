import random
import json
import hashlib
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from questions.models import Subject, Question, Tag
from django.db import transaction

class Command(BaseCommand):
    help = 'Populates the database with sample subjects, questions, and tags.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        with transaction.atomic(): # Use a transaction for atomicity
            # Clear existing data (optional, be careful with this in production)
            # self.stdout.write(self.style.WARNING('Clearing existing Question, Subject, and Tag data...'))
            # Question.objects.all().delete()
            # Subject.objects.all().delete()
            # Tag.objects.all().delete()

            # Create Tags
            tag_names = ["基礎", "進階", "常識", "語法", "詞彙", "數學", "科學", "歷史", "地理", "編程"]
            tags = {}
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                tags[name] = tag
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created tag: {name}'))

            # Define Subjects data
            subjects_data = [
                {
                    "name": "綜合知識模擬測驗 (A)",
                    "description": "包含各種常識、科學和文法問題的綜合測驗。",
                    "price": 10.00,
                    "trial_questions_count": 5
                },
                {
                    "name": "數學與邏輯挑戰 (B)",
                    "description": "一系列數學題目和邏輯推理問題，考驗您的分析能力。",
                    "price": 15.00,
                    "trial_questions_count": 3
                }
            ]

            for subject_data in subjects_data:
                subject, created = Subject.objects.get_or_create(
                    name=subject_data["name"],
                    defaults={
                        'description': subject_data["description"],
                        'price': subject_data["price"],
                        'trial_questions_count': subject_data["trial_questions_count"]
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created subject: {subject.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Subject "{subject.name}" already exists.'))

                num_questions_to_create = 50
                questions_created_for_subject = 0

                for i in range(num_questions_to_create):
                    question_type = random.choice(['single_choice', 'multiple_choice', 'fill_in_blank'])
                    difficulty = random.choice(['easy', 'medium', 'hard'])
                    content = f'{subject.name} - 題目 {i+1} ({_(question_type)}, {_(difficulty)}): 這是一個關於...的問題？'
                    
                    options_data = None
                    correct_answer_data = ""
                    
                    if question_type == 'single_choice':
                        num_options = 4
                        opts = {slugify(f'選項{chr(65+j)}{i+1}'): f'選項 {chr(65+j)} - 這是答案選項{j+1}。' for j in range(num_options)}
                        options_data = opts
                        correct_answer_data = random.choice(list(opts.keys()))
                        content = f'{subject.name} - 單選題 {i+1} ({_(difficulty)}): 以下哪個是正確的？'

                    elif question_type == 'multiple_choice':
                        num_options = 5
                        opts = {slugify(f'選項{chr(65+j)}{i+1}'): f'選項 {chr(65+j)} - 多選答案選項{j+1}。' for j in range(num_options)}
                        options_data = opts
                        # Correct answer is a list of 1 to 3 random option keys
                        num_correct = random.randint(1, min(3, num_options))
                        correct_keys = random.sample(list(opts.keys()), num_correct)
                        correct_answer_data = json.dumps(sorted(correct_keys))
                        content = f'{subject.name} - 多選題 {i+1} ({_(difficulty)}): 選擇所有正確的陳述。'

                    elif question_type == 'fill_in_blank':
                        options_data = None # No predefined options for fill_in_blank via JSONField
                        correct_answer_data = f'正確答案{i+1}'
                        content = f'{subject.name} - 填空題 {i+1} ({_(difficulty)}): ____ 是宇宙的答案。'

                    # Generate a unique hash based on critical fields to prevent exact duplicates if script is run multiple times
                    hash_content = f'{subject.id}{content}{json.dumps(options_data, sort_keys=True)}{correct_answer_data}{difficulty}{question_type}'
                    question_hash = hashlib.sha256(hash_content.encode('utf-8')).hexdigest()

                    # Check if a question with this hash already exists for this subject
                    if Question.objects.filter(question_hash=question_hash, subject=subject).exists():
                        # self.stdout.write(self.style.WARNING(f'Skipping duplicate question (hash conflict): {content[:50]}...'))
                        continue # Skip creating this question if it's a duplicate for this subject
                    
                    try:
                        question = Question.objects.create(
                            subject=subject,
                            content=content,
                            options=options_data,
                            correct_answer=correct_answer_data,
                            explanation=f'這是題目 {i+1} 的詳細解析。我們解釋了為什麼答案是這樣，並提供相關背景知識。' if random.random() > 0.3 else None, # Randomly add explanation
                            is_ai_generated=random.choice([True, False]),
                            difficulty=difficulty,
                            question_type=question_type,
                            question_hash=question_hash
                        )
                        
                        # Add 1 to 3 random tags
                        num_tags_to_add = random.randint(1, 3)
                        selected_tag_keys = random.sample(list(tags.keys()), num_tags_to_add)
                        for tag_key in selected_tag_keys:
                            question.tags.add(tags[tag_key])
                        
                        questions_created_for_subject += 1
                        # self.stdout.write(self.style.SUCCESS(f'  Successfully created question {questions_created_for_subject}/{num_questions_to_create} for {subject.name}'))
                        if questions_created_for_subject >= num_questions_to_create:
                            break # Reached desired number of questions for this subject

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating question {i+1} for {subject.name}: {e}'))
                
                self.stdout.write(self.style.SUCCESS(f'Finished creating {questions_created_for_subject} questions for subject: {subject.name}'))

        self.stdout.write(self.style.SUCCESS('Data population complete!')) 