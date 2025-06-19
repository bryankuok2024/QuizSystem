from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import F, Prefetch, Count, Q, Subquery, OuterRef, Exists
from .forms import QuestionForm, QuestionAnswerForm
from .models import Question, Subject, Tag, MajorSubject, Bookmark
from .utils import decode_id, encode_id
from users.models import UserSubjectPurchase
from progress.models import UserProgress, UserAnswerLog
import hashlib
import json
import random
from django.views.generic import ListView, DetailView, View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from .filters import QuestionFilter

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
    # This view handles both displaying questions (GET) and processing answers (POST)
    
    # POST request: process submitted answers
    if request.method == 'POST':
        # Determine the practice mode from the submitted form
        practice_mode = request.POST.get('practice_mode', 'subject')
        
        presented_ids_str = request.POST.get('presented_question_ids', '')
        presented_q_ids = [int(id_str) for id_str in presented_ids_str.split(',') if id_str]
        
        questions = Question.objects.select_related('subject').filter(id__in=presented_q_ids)
        
        score = 0
        results_data = []
        answer_logs_to_create = []
        
        # New robust progress tracking logic
        progress_cache = {}
        subject_stats = {}

        subject = None
        # Subject-specific logic, only relevant if not in wrong_questions mode
        if practice_mode == 'subject':
            subject_id = request.POST.get('subject_id')
            if not subject_id:
                messages.error(request, "练习提交无效，缺少科目ID。")
                return redirect('pages:home')
            subject = get_object_or_404(Subject, pk=subject_id)

        for question in questions:
            subject_id = question.subject.id
            # Cache UserProgress objects to avoid repeated DB queries
            if subject_id not in progress_cache:
                progress, created = UserProgress.objects.get_or_create(user=request.user, subject=question.subject)
                progress_cache[subject_id] = progress
            progress = progress_cache[subject_id]

            # Initialize stats for the subject if not present
            if subject_id not in subject_stats:
                subject_stats[subject_id] = {'correct': 0, 'answered': 0}

            is_correct = False
            options_dict = question.options or {}
            user_answer_keys = request.POST.getlist(f'question_{question.id}')

            if question.question_type == 'single_choice':
                user_answer_key = user_answer_keys[0] if user_answer_keys else None
                correct_answer_from_db = str(question.correct_answer or '').strip()
                
                user_answer_value = ""
                if user_answer_key:
                    user_answer_value = str(options_dict.get(user_answer_key) or '').strip()

                is_correct_by_key = (user_answer_key is not None and user_answer_key.strip().lower() == correct_answer_from_db.lower())
                is_correct_by_value = (user_answer_value != "" and user_answer_value.lower() == correct_answer_from_db.lower())
                is_correct = is_correct_by_key or is_correct_by_value

                user_answer_display = options_dict.get(user_answer_key, "未作答")
                correct_answer_display = options_dict.get(correct_answer_from_db, correct_answer_from_db)
            
            elif question.question_type == 'multiple_choice':
                correct_answer_list = []
                if question.correct_answer:
                    raw_answer_str = str(question.correct_answer)
                    try:
                        loaded_answers = json.loads(raw_answer_str)
                        if isinstance(loaded_answers, list):
                            correct_answer_list = loaded_answers
                    except json.JSONDecodeError:
                        cleaned_str = raw_answer_str.strip().replace('[', '').replace(']', '').replace('"', '').replace("'", "")
                        correct_answer_list = [item.strip() for item in cleaned_str.split(',') if item.strip()]

                user_keys_set = {str(k).strip().lower() for k in user_answer_keys}
                db_items_set = {str(i).strip().lower() for i in correct_answer_list}
                
                is_correct_by_key = (user_keys_set == db_items_set)
                
                user_values_set = {str(options_dict.get(k) or '').strip().lower() for k in user_answer_keys if options_dict.get(k)}
                is_correct_by_value = (user_values_set and user_values_set == db_items_set)

                is_correct = is_correct_by_key or is_correct_by_value
                
                user_answer_display = ", ".join(sorted([options_dict.get(k, k) for k in user_answer_keys])) if user_answer_keys else "未作答"
                correct_answer_display_keys = [str(k) for k in correct_answer_list]
                correct_answer_display = ", ".join(sorted([options_dict.get(k, k) for k in correct_answer_display_keys]))

            elif question.question_type == 'fill_in_blank':
                user_answer_text = user_answer_keys[0] if user_answer_keys else ""
                is_correct = (user_answer_text.strip().lower() == question.correct_answer.strip().lower())
                user_answer_display = user_answer_text if user_answer_text else "未作答"
                correct_answer_display = question.correct_answer
            
            else: # Fallback for unknown types
                user_answer_display = "N/A"
                correct_answer_display = "N/A"

            subject_stats[subject_id]['answered'] += 1
            if is_correct:
                score += 1
                subject_stats[subject_id]['correct'] += 1
            
            # Log every answer attempt if an answer was provided
            if user_answer_keys:
                answer_logs_to_create.append(
                    UserAnswerLog(progress=progress, question=question, is_correct=is_correct)
                )

            results_data.append({
                'question': question,
                'user_answer': user_answer_display,
                'is_correct': is_correct,
                'correct_answer_display': correct_answer_display,
            })
        
        # After loop, bulk create all answer logs for efficiency
        if answer_logs_to_create:
            UserAnswerLog.objects.bulk_create(answer_logs_to_create)

        # Update UserProgress only if in 'subject' practice mode to avoid double counting
        if practice_mode == 'subject':
            for subject_id, stats in subject_stats.items():
                if stats['answered'] > 0:
                    progress_to_update = progress_cache[subject_id]
                    progress_to_update.total_questions_answered = F('total_questions_answered') + stats['answered']
                    progress_to_update.total_correct_answers = F('total_correct_answers') + stats['correct']
                    progress_to_update.last_practice_session_score = round((stats['correct'] / stats['answered']) * 100)
                    progress_to_update.last_practiced_at = timezone.now()
                    
                    # This might not be perfectly atomic if done this way without select_for_update,
                    # but for this quiz application's load, it's a reasonable trade-off.
                    # We fetch it again to compare the score.
                    # A more robust solution might involve a database transaction.
                    current_highest = progress_to_update.highest_score or 0
                    if progress_to_update.last_practice_session_score > current_highest:
                        progress_to_update.highest_score = progress_to_update.last_practice_session_score

                    progress_to_update.save()
        
        # Prepare context for the results display, which is part of the same template now
        total_questions_submitted = len(presented_q_ids)
        percentage = round((score / total_questions_submitted) * 100) if total_questions_submitted > 0 else 0

        # 将结果存储在session中以便重定向后可以获取
        request.session['practice_results'] = {
            'score': score,
            'total': total_questions_submitted,
            'percentage': percentage,
            'subject_id': subject.id if subject else None,
        }

        return redirect('questions:practice_result')

    # GET request: display questions
    hashed_subject_id = request.GET.get('subject')
    subject_id = None
    if hashed_subject_id:
        subject_id = decode_id(hashed_subject_id)

    if subject_id:
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            messages.error(request, _("您嘗試存取的科目不存在或已被移除。"))
            return redirect('pages:home')

        # Handle progress reset - now it should delete the logs and reset summary
        if request.GET.get('reset') == 'true':
            progress = UserProgress.objects.filter(user=request.user, subject=subject).first()
            if progress:
                # Delete all previous logs for this subject
                UserAnswerLog.objects.filter(progress=progress).delete()
                # Reset the progress summary fields
                progress.total_questions_answered = 0
                progress.total_correct_answers = 0
                progress.last_practice_session_score = 0
                progress.highest_score = 0
                progress.save()
                messages.success(request, _("已重置「{}」科目的練習記錄。").format(subject.name))
            # Redirect with the hashed ID
            return redirect(f"{request.path_info}?subject={encode_id(subject.id)}")

        # --- Final, Corrected Security and Content Logic ---
        is_purchased = UserSubjectPurchase.objects.filter(user=request.user, subject=subject).exists()
        is_free = subject.price == 0
        questions = []

        if is_purchased or is_free:
            # Full access if purchased or the subject is free
            questions = list(subject.questions.all())
        else:
            # For non-purchased, paid subjects, only provide trial questions if they exist
            questions = list(subject.questions.filter(is_trial=True))
            if not questions:
                # If there are no trial questions, block access and inform the user
                messages.warning(request, _("「{}」科目沒有可用的試玩題目，請購買以解鎖所有內容。").format(subject.name))
                return redirect('questions:subject_list')
        
        # --- End of Logic ---

        random.shuffle(questions)
        
        # Add correct_answer_json to each question object
        for question in questions:
            # Prepare shuffled options for display
            options_list = []
            if isinstance(question.options, dict):
                options_list = list(question.options.items())
                random.shuffle(options_list)
            question.shuffled_options_list = options_list
            
            # Prepare correct answer for the "show answer" feature
            question.correct_answer_json = question.get_correct_answer_as_json()

        context = {
            'selected_subject': subject,
            'subject_name': subject.name,
            'questions': questions,
            'question_ids_str': ",".join([str(q.id) for q in questions]),
            'is_purchased': is_purchased,
            'results_mode': False,
            'practice_mode': 'subject',
        }
        return render(request, 'questions/practice_quiz_interface.html', context)
    
    # If no subject_id, show the subject selection page or handle as a random quiz
    messages.info(request, _("請先選擇一個科目開始練習。"))
    return redirect('pages:home')

@login_required
def practice_result_view(request):
    """显示练习结果的独立页面"""
    if 'practice_results' not in request.session:
        # 如果session中没有结果，可能是用户直接访问URL，重定向到主页
        return redirect('pages:home')
    
    # 从session中清除结果，这样刷新页面就不会再次看到旧结果
    # context = {'results': request.session.pop('practice_results')}

    return render(request, 'questions/practice_result.html')

class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = "questions/subject_list.html"
    context_object_name = "subjects"

    def get_queryset(self):
        # Correct the optimization: prefetch the related MajorSubject for each Subject
        return Subject.objects.filter(is_published=True).select_related('major_subject')


class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject
    template_name = "questions/subject_detail.html"
    context_object_name = "subject"

    def get(self, request, *args, **kwargs):
        hashed_id = kwargs.get('hashed_id')
        subject_id = decode_id(hashed_id)

        if subject_id is None:
            messages.error(request, _("無效的科目連結。"))
            return redirect('questions:subject_list')

        try:
            # Use the decoded ID to fetch the object
            self.object = self.get_queryset().get(pk=subject_id)
        except self.model.DoesNotExist:
            messages.error(request, _("您嘗試存取的科目不存在或已被移除。"))
            return redirect('questions:subject_list')
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_queryset(self):
        # Only show published subjects
        return Subject.objects.filter(is_published=True)

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

class PracticeQuestionView(LoginRequiredMixin, View):
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

    def get(self, request, hashed_id):
        question_pk = decode_id(hashed_id)
        if question_pk is None:
            messages.error(request, _("無效的題目連結。"))
            return redirect('questions:subject_list')

        try:
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            messages.error(request, _("您嘗試存取的題目不存在或已被移除。"))
            return redirect('questions:subject_list')
        
        subject = question.subject

        # --- Security Check ---
        # Allow access if subject is free, purchased, or the question is a trial question.
        is_purchased = UserSubjectPurchase.objects.filter(user=request.user, subject=subject).exists()
        is_free = subject.price == 0
        is_trial_question = question.is_trial

        if not (is_purchased or is_free or is_trial_question):
            messages.error(request, _("您需要先購買「{}」科目才能練習此題目。").format(subject.name))
            return redirect('questions:subject_list')
        # --- End Security Check ---
        
        form = None
        # The old trial logic below is no longer needed here as it's handled by the security check above.
        options_for_form = self.get_options_for_form(question)
        form = QuestionAnswerForm(options=options_for_form, question_type=question.question_type)
        
        context = {
            'question': question,
            'form': form,
            'is_answered': False,
            'trial_limit_message': None, # This logic is simplified/removed for now
            'can_practice_question': True,
        }
        return render(request, self.template_name, context)

    def post(self, request, hashed_id):
        question_pk = decode_id(hashed_id)
        if question_pk is None:
            return JsonResponse({'error': '無效的題目連結。'}, status=404)

        try:
            question = Question.objects.get(pk=question_pk)
        except Question.DoesNotExist:
            return JsonResponse({'error': '您嘗試回答的題目不存在或已被移除。'}, status=404)
        
        # --- Security Check ---
        # Also protect the POST request to ensure no unauthorized answers are submitted.
        subject = question.subject
        is_purchased = UserSubjectPurchase.objects.filter(user=request.user, subject=subject).exists()
        is_free = subject.price == 0
        is_trial_question = question.is_trial

        if not (is_purchased or is_free or is_trial_question):
            return JsonResponse({'error': '您沒有權限回答此問題。'}, status=403)
        # --- End Security Check ---

        form = QuestionAnswerForm(request.POST, question=question)

        if form.is_valid():
            is_correct = form.cleaned_data['answer'] == question.correct_answer
            message = _("正确！") if is_correct else _("错误。正确答案是: {}").format(question.correct_answer)
            
            if is_correct and request.user.is_authenticated:
                progress, created = UserProgress.objects.get_or_create(
                    user=request.user,
                    subject=question.subject
                )
                if not created:
                    progress.completed_questions_count = F('completed_questions_count') + 1
                    progress.correct_answers_count = F('correct_answers_count') + 1
                    progress.save(update_fields=['completed_questions_count', 'correct_answers_count', 'updated_at'])
                else:
                    # If created, the defaults in the model are 0, so we need to set them.
                    # Or better, handle it in get_or_create defaults
                    progress.completed_questions_count = 1
                    progress.correct_answers_count = 1
                    progress.save()


            return JsonResponse({'correct': is_correct, 'message': message, 'explanation': question.explanation})
        else:
            return JsonResponse({'error': form.errors}, status=400)

@login_required
def wrong_questions_practice_view(request):
    """
    错题本练习视图
    查询用户所有答错的题目,并启动一个练习会话
    """
    user = request.user
    # 查找用户所有答错的记录, 获取不重复的题目ID
    wrong_question_ids = UserAnswerLog.objects.filter(
        progress__user=user, 
        is_correct=False
    ).values_list('question_id', flat=True).distinct()

    if not wrong_question_ids:
        messages.info(request, "恭喜您！目前沒有錯題記錄。")
        return redirect('pages:home')

    # 获取问题对象,并预加载相关的科目信息以备后用
    questions = list(Question.objects.select_related('subject').filter(id__in=wrong_question_ids))
    random.shuffle(questions)

    # 为每个问题创建并附加打乱后的选项列表，并加上 correct_answer_json
    for question in questions:
        options_list = []
        if isinstance(question.options, dict):
            options_list = list(question.options.items())
            random.shuffle(options_list)
        question.shuffled_options_list = options_list
        # 新增：加上 correct_answer_json
        question.correct_answer_json = question.get_correct_answer_as_json()

    question_ids = [q.id for q in questions]

    context = {
        'questions': questions,
        'subject_name': "我的錯題本",
        'total_questions': len(questions),
        'question_ids_str': ",".join(map(str, question_ids)),
        'practice_mode': 'wrong_questions',  # Pass the mode to the template so the form can use it
    }
    return render(request, 'questions/practice_quiz_interface.html', context)

@login_required
def toggle_bookmark_view(request, hashed_id):
    question_id = decode_id(hashed_id)
    if question_id is None:
        return JsonResponse({'status': 'error', 'message': '無效的題目ID'}, status=400)

    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)

        if not created:
            # If the bookmark already existed, this means the user wants to remove it.
            bookmark.delete()
            return JsonResponse({'status': 'success', 'bookmarked': False})
        else:
            # If the bookmark was just created.
            return JsonResponse({'status': 'success', 'bookmarked': True})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def question_search_view(request):
    # 1. 确定用户有权访问的科目
    # 首先获取所有免费科目的ID
    accessible_subject_ids = set(
        Subject.objects.filter(price=0).values_list('id', flat=True)
    )
    # 然后添加用户已购买的科目ID
    purchased_subjects_ids = UserSubjectPurchase.objects.filter(
        user=request.user
    ).values_list('subject_id', flat=True)
    accessible_subject_ids.update(purchased_subjects_ids)

    # 2. 基于有权访问的科目来筛选题目
    # 使用 Exists 子查询来标注用户是否收藏了该题目
    bookmark_subquery = Bookmark.objects.filter(
        question_id=OuterRef('pk'),
        user=request.user
    )
    
    # 从有权限的题目开始构建查询
    question_list = Question.objects.filter(
        subject_id__in=list(accessible_subject_ids)
    ).annotate(
        is_bookmarked=Exists(bookmark_subquery)
    ).select_related('subject').prefetch_related('tags').order_by('-created_at')

    question_filter = QuestionFilter(request.GET, queryset=question_list)
    
    paginator = Paginator(question_filter.qs, 25)  # 每页显示 25 个
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'filter': question_filter,
        'page_obj': page_obj,
    }
    return render(request, 'questions/question_search.html', context)

@login_required
def bookmarks_list_view(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('question', 'question__subject')
    
    paginator = Paginator(bookmarks, 25) # 每页显示 25 个
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'questions/bookmark_list.html', context)

# def add_question_view(request):
#     return HttpResponse("This is a placeholder for add_question_view in quizApp/questions.") 