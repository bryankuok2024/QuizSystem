from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import QuestionForm
from .models import Question, Subject
import hashlib
import json
import random

# Create your views here.

def question_list(request):
    """題目列表頁面"""
    return render(request, 'questions/question_list.html')

@login_required
def quiz(request):
    """開始測驗"""
    return render(request, 'questions/quiz.html')

@login_required
def create_question(request):
    """創建題目"""
    return render(request, 'questions/create_question.html')

@login_required
def add_question_view(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question_instance = form.save(commit=False)
            
            content_to_hash = (
                str(question_instance.subject_id) +
                question_instance.content +
                json.dumps(question_instance.options, sort_keys=True) +
                question_instance.correct_answer +
                question_instance.difficulty +
                question_instance.question_type
            )
            
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                image_file.seek(0)
                image_content = image_file.read()
                content_to_hash += hashlib.sha256(image_content).hexdigest()
                image_file.seek(0)

            question_instance.question_hash = hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()
            
            if not question_instance.pk and Question.objects.filter(question_hash=question_instance.question_hash).exists():
                messages.error(request, _('错误：与此题目内容相似的题目已存在 (哈希冲突)。'))
                return render(request, 'questions/add_question.html', {'form': form})
            
            try:
                question_instance.save()
                form.save_m2m()
                messages.success(request, _('题目已成功添加！'))
                return redirect('questions:add_question')
            except Exception as e:
                messages.error(request, _('保存题目时发生错误: {}').format(str(e)))
        else:
            messages.error(request, _('表单数据无效，请检查错误信息。'))
    else:
        form = QuestionForm()
    
    return render(request, 'questions/add_question.html', {'form': form})

@login_required
def practice_quiz_view(request):
    """
    Handles the practice quiz:
    - GET without subject_id: Shows subject selection.
    - GET with subject_id: Shows quiz interface for the selected subject.
    - POST (from subject selection): Fetches questions for the selected subject.
    - POST (from quiz submission): Processes answers and shows results.
    """
    if request.method == 'POST':
        # Logic for handling POST requests (subject selection or answer submission)
        subject_id = request.POST.get('subject_id')
        if subject_id:
            try:
                subject = Subject.objects.get(pk=subject_id)
                # Redirect to the GET URL for the quiz with the subject_id
                # This helps maintain a clean URL and allows bookmarking the quiz start.
                return redirect(f"{request.path}?subject_id={subject.id}")
            except Subject.DoesNotExist:
                messages.error(request, _("所選科目不存在。"))
                return redirect(request.path) # Redirect back to subject selection
        
        # Placeholder for answer submission processing
        # This part will be more complex and involve fetching submitted answers,
        # comparing them, calculating a score, etc.
        
        # For now, let's assume we're re-displaying the form or showing results.
        # We'll need to retrieve the subject_id from a hidden field or session
        # if we are processing answers.
        
        # Example: if 'quiz_submission' in request.POST:
        #   process_answers(request)
        #   return render(request, 'questions/practice_quiz_interface.html', context_with_results)
        
        # If it's not a recognized POST action, or something went wrong,
        # redirect to subject selection.
        return redirect(request.path)

    # --- Handle GET requests ---
    subject_id = request.GET.get('subject_id')
    if subject_id:
        try:
            subject = Subject.objects.get(pk=subject_id)
            questions = Question.objects.filter(subject=subject).order_by('?') # Get random questions for now
            
            # Basic context for now, will be expanded
            context = {
                'subject': subject,
                'questions': [], # Will be populated with processed questions
                'is_quiz_active': True,
            }

            processed_questions = []
            for question in questions:
                options = question.options
                shuffled_options_list = []
                correct_answer_value = question.correct_answer

                if isinstance(options, dict):
                    # Handle dictionary options (e.g., {"A": "Option 1", "B": "Option 2"})
                    # Ensure correct_answer_value matches one of the keys if it's a single letter
                    # Or, if correct_answer is the full text, we'll need to adapt.
                    # For now, assume correct_answer is a key like 'A'.
                    
                    # Convert dict to list of tuples for shuffling and consistent template access
                    options_list = list(options.items())
                    random.shuffle(options_list)
                    shuffled_options_list = options_list

                elif isinstance(options, list):
                    # Handle list options (e.g., ["Option 1", "Option 2"])
                    # Here, correct_answer is likely the full text of the correct option.
                    
                    # Convert list to list of tuples (index, value) or just keep as list
                    # For template consistency, let's make it list of (original_index, value)
                    # This isn't strictly necessary if the template can handle simple lists.
                    # For now, let's assume the template will iterate and use `forloop.counter` if needed
                    # or we provide a simple list of strings.
                    
                    temp_options = list(options) # Create a mutable copy
                    random.shuffle(temp_options)
                    shuffled_options_list = [(str(i), opt) for i, opt in enumerate(temp_options)] # Giving pseudo-keys

                else:
                    # Fallback or error for unknown options format
                    shuffled_options_list = [] # Or handle error appropriately

                processed_questions.append({
                    'id': question.id,
                    'content': question.content,
                    'image_url': question.image.url if question.image else None,
                    'question_type': question.question_type,
                    'shuffled_options_list': shuffled_options_list,
                    '#correct_answer': correct_answer_value, # Keep for grading, not for direct display unless reviewing
                    'explanation': question.explanation,
                })
            context['questions'] = processed_questions
            return render(request, 'questions/practice_quiz_interface.html', context)
        except Subject.DoesNotExist:
            messages.error(request, _("所選科目不存在。"))
            return redirect(request.path) # Redirect to subject selection
    else:
        # No subject_id, show subject selection page
        subjects = Subject.objects.all()
        context = {
            'subjects': subjects,
            'is_quiz_active': False,
        }
        return render(request, 'questions/practice_subject_selection.html', context)

# def add_question_view(request):
#     return HttpResponse("This is a placeholder for add_question_view in quizApp/questions.") 