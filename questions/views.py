from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import QuestionForm, QuestionAnswerForm
from .models import Question, Subject
from users.models import UserSubjectPurchase
import hashlib
import json
import random
from django.views.generic import ListView, DetailView, View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    - POST (from subject selection): This is now handled by GET with query param.
    - POST (from quiz submission): Processes answers and shows results.
    """
    if request.method == 'POST' and request.POST.get('action') == 'submit_answers':
        subject_id = request.POST.get('subject_id')
        try:
            subject = get_object_or_404(Subject, pk=subject_id)
            # Fetch all question IDs that could have been in the quiz to validate submissions
            all_question_ids_for_subject = list(Question.objects.filter(subject=subject).values_list('id', flat=True))
            
            questions_with_results = []
            score = 0
            total_questions = 0

            for q_id in all_question_ids_for_subject:
                # Construct the key for the submitted answer for this question
                answer_key = f'question_{q_id}'
                if answer_key in request.POST:
                    total_questions += 1
                    question = get_object_or_404(Question, pk=q_id)
                    
                    is_correct = False
                    user_answer_for_display = ""
                    
                    if question.question_type == 'multiple_choice':
                        user_answers = request.POST.getlist(answer_key)
                        # Normalize correct answer: "A, C" -> {"A", "C"}
                        correct_answer_set = set(ans.strip() for ans in str(question.correct_answer).split(','))
                        # Normalize user answer: ["A", "C"] -> {"A", "C"}
                        user_answer_set = set(user_answers)
                        is_correct = (correct_answer_set == user_answer_set)
                        user_answer_for_display = ", ".join(sorted(user_answers))
                    else:
                        # Logic for single choice, fill-in-the-blank etc.
                        user_answer = request.POST.get(answer_key)
                        is_correct = (str(user_answer).lower() == str(question.correct_answer).lower())
                        if question.question_type == 'single_choice' and isinstance(question.options, dict):
                            user_answer_for_display = question.options.get(user_answer, user_answer)
                        else:
                            user_answer_for_display = user_answer

                    if is_correct:
                        score += 1
                    
                    correct_answer_display = question.correct_answer
                    # For single_choice, we might want to display the option text instead of just "A"
                    if question.question_type == 'single_choice' and isinstance(question.options, dict):
                        correct_answer_display = question.options.get(question.correct_answer, question.correct_answer)
                    # For multiple_choice, we can format it nicely
                    elif question.question_type == 'multiple_choice':
                        correct_answer_display = ", ".join(sorted([ans.strip() for ans in str(question.correct_answer).split(',')]))

                    questions_with_results.append({
                        'question': question,
                        'user_answer': user_answer_for_display,
                        'is_correct': is_correct,
                        'correct_answer_display': correct_answer_display,
                         # Pass shuffled options again for result display consistency
                        'shuffled_options_list': list(question.options.items()) if isinstance(question.options, dict) else [],
                    })

            percentage = round((score / total_questions) * 100) if total_questions > 0 else 0

            context = {
                'results_mode': True,
                'selected_subject': subject,
                'score': score,
                'total_questions': total_questions,
                'percentage': percentage,
                'questions_with_results': questions_with_results,
            }
            return render(request, 'questions/practice_quiz_interface.html', context)

        except Subject.DoesNotExist:
            messages.error(request, _("提交的科目不存在。"))
            return redirect('questions:practice_quiz')

    # --- Handle GET requests ---
    subject_id = request.GET.get('subject_id')
    if subject_id:
        try:
            subject = Subject.objects.get(pk=subject_id)
            all_questions_query = Question.objects.filter(subject=subject)

            # --- Trial Logic Implementation ---
            is_purchased = False
            if request.user.is_authenticated:
                is_purchased = UserSubjectPurchase.objects.filter(user_id=request.user.pk, subject=subject).exists()

            trial_limit_reached = False
            questions_for_practice = all_questions_query

            if subject.price > 0 and not is_purchased:
                # It's a paid subject and user hasn't purchased it.
                trialed_questions_by_subject = request.session.get('trialed_questions_by_subject', {})
                trialed_ids = trialed_questions_by_subject.get(str(subject.id), [])
                
                # Exclude already trialed questions
                questions_for_practice = all_questions_query.exclude(id__in=trialed_ids)
                
                remaining_trials = subject.trial_questions_count - len(trialed_ids)
                if remaining_trials <= 0:
                    trial_limit_reached = True
                    questions_for_practice = Question.objects.none() # No more questions
                else:
                    # Limit the number of new trial questions
                    questions_for_practice = list(questions_for_practice.order_by('?')[:remaining_trials])
            else:
                # Free subject or purchased subject, get all questions randomly
                questions_for_practice = list(all_questions_query.order_by('?'))


            # Storing trialed questions in session after they've been selected for the quiz
            if subject.price > 0 and not is_purchased and not trial_limit_reached:
                trialed_questions_by_subject = request.session.get('trialed_questions_by_subject', {})
                # Ensure the key exists
                if str(subject.id) not in trialed_questions_by_subject:
                    trialed_questions_by_subject[str(subject.id)] = []
                
                newly_trialed_ids = [q.id for q in questions_for_practice]
                # Add new questions to the session, avoiding duplicates
                existing_ids = set(trialed_questions_by_subject[str(subject.id)])
                existing_ids.update(newly_trialed_ids)
                trialed_questions_by_subject[str(subject.id)] = list(existing_ids)
                
                request.session['trialed_questions_by_subject'] = trialed_questions_by_subject
                request.session.modified = True


            context = {
                'selected_subject': subject,
                'questions': [], # Will be populated with processed questions
                'is_quiz_active': True,
                'is_purchased': is_purchased,
                'trial_limit_reached': trial_limit_reached,
                'trial_questions_count': subject.trial_questions_count if subject.price > 0 else 0,
            }

            processed_questions = []
            for question in questions_for_practice: # Use the filtered and limited list
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

class SubjectListView(ListView):
    model = Subject
    template_name = 'questions/subject_list.html'
    context_object_name = 'subjects'
    queryset = Subject.objects.all() # Explicitly define queryset for clarity

class SubjectDetailView(DetailView):
    model = Subject
    template_name = 'questions/subject_detail.html'
    context_object_name = 'subject'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.get_object()
        question_list = Question.objects.filter(subject=subject).order_by('created_at') # Or any other preferred order
        
        paginator = Paginator(question_list, 10) # Show 10 questions per page
        page_number = self.request.GET.get('page')
        
        try:
            questions_page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            questions_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            questions_page = paginator.page(paginator.num_pages)
            
        context['questions_page'] = questions_page
        return context

class PracticeQuestionView(View):
    template_name = 'questions/practice_question.html'

    def get_options_for_form(self, question):
        """Helper to format options for the form."""
        options_for_form = []
        if isinstance(question.options, dict): # e.g., {"A": "Text A", "B": "Text B"}
            options_for_form = list(question.options.items())
        elif isinstance(question.options, list): # e.g., ["Text A", "Text B"]
            # For lists, use the value itself as both key and display value,
            # or generate simple keys if needed by the form/comparison logic.
            # Assuming correct_answer will be the full text for list-type options.
            options_for_form = [(opt, opt) for opt in question.options]
        return options_for_form

    def get(self, request, question_pk):
        question = get_object_or_404(Question, pk=question_pk)
        subject = question.subject
        trial_limit_message = None
        can_practice_question = True # Assume user can practice by default

        # Initialize session for trialed questions if not present
        # Structure: {'trialed_questions_by_subject': { 'subject_id_str': [q_id1, q_id2] } }
        trialed_questions_by_subject = request.session.get('trialed_questions_by_subject', {})
        
        # Get trialed questions for the current subject
        # Ensure subject.id is a string key for session consistency
        trialed_ids_for_current_subject = trialed_questions_by_subject.get(str(subject.id), [])

        if subject.price > 0 and hasattr(subject, 'trial_questions_count') and subject.trial_questions_count > 0:
            # This is a paid subject with a defined trial limit
            is_already_trialed = question.id in trialed_ids_for_current_subject

            if not is_already_trialed:
                if len(trialed_ids_for_current_subject) >= subject.trial_questions_count:
                    # Limit reached for new trial questions
                    trial_limit_message = _(
                        "您对科目'{subject_name}'的试玩题目数量已达到上限 ({count}道)。请考虑购买以解锁所有题目。"
                    ).format(subject_name=subject.name, count=subject.trial_questions_count)
                    can_practice_question = False # Cannot practice this new question
                else:
                    # It's a new trial question and within limit
                    trialed_ids_for_current_subject.append(question.id)
                    trialed_questions_by_subject[str(subject.id)] = trialed_ids_for_current_subject
                    request.session['trialed_questions_by_subject'] = trialed_questions_by_subject
                    request.session.modified = True # Ensure session is saved
            # else: pass, it's already trialed, allow access (can_practice_question remains True)
        
        form = None
        if can_practice_question:
            options_for_form = self.get_options_for_form(question)
            form = QuestionAnswerForm(options=options_for_form, question_type=question.question_type)
        
        context = {
            'question': question,
            'form': form, # Will be None if trial limit reached for a new question
            'is_answered': False,
            'trial_limit_message': trial_limit_message,
            'can_practice_question': can_practice_question, # Pass this to template
        }
        return render(request, self.template_name, context)

    def post(self, request, question_pk):
        question = get_object_or_404(Question, pk=question_pk)
        options_for_form = self.get_options_for_form(question)
        form = QuestionAnswerForm(request.POST, options=options_for_form, question_type=question.question_type)
        
        is_correct = False
        user_answer = None
        correct_answer_for_display_text = str(question.correct_answer) # Default

        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            
            if question.question_type == 'multiple_choice':
                correct_answers_set = set(ans.strip() for ans in question.correct_answer.split(','))
                user_answers_set = set(user_answer)
                is_correct = (correct_answers_set == user_answers_set)
                # Prepare display text for multiple choice correct answers
                if isinstance(question.options, dict):
                    texts = [f"{k}: {v}" for k, v in question.options.items() if k in correct_answers_set]
                    correct_answer_for_display_text = ", ".join(texts)
                else: # Assuming correct_answer contains the literal answers if options is a list
                    correct_answer_for_display_text = question.correct_answer
            else: # Single choice and fill-in-the-blank
                is_correct = (str(user_answer) == str(question.correct_answer))
                if question.question_type == 'single_choice' and isinstance(question.options, dict):
                    correct_answer_for_display_text = question.options.get(question.correct_answer, str(question.correct_answer))
                    if correct_answer_for_display_text != str(question.correct_answer):
                         correct_answer_for_display_text += f" ({question.correct_answer})"
                else:
                    correct_answer_for_display_text = str(question.correct_answer)
        
        context = {
            'question': question,
            'form': form, 
            'is_answered': True,
            'is_correct': is_correct,
            'user_answer': user_answer, 
            'correct_answer_display': correct_answer_for_display_text, # Use the processed text
        }
        
        # This specific block for multiple choice text list might still be useful if template iterates it
        if question.question_type == 'multiple_choice' and isinstance(question.options, dict):
            correct_keys = set(ans.strip() for ans in question.correct_answer.split(','))
            context['correct_options_text_list'] = [f"{key}: {value}" for key, value in question.options.items() if key in correct_keys]


        return render(request, self.template_name, context)

# def add_question_view(request):
#     return HttpResponse("This is a placeholder for add_question_view in quizApp/questions.") 