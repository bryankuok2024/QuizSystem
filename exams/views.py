import random
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import Http404

from .models import ExamSession
from questions.models import Subject, Question
from progress.models import UserProgress
from questions.utils import decode_hashid, hash_id

# 一次模擬考試抽取的題目數量
EXAM_QUESTIONS_COUNT = 10

class StartExamView(LoginRequiredMixin, View):
    """
    處理開始一場新考試的請求。
    """
    def get(self, request, *args, **kwargs):
        hashed_id = self.kwargs.get('hashed_id')
        subject_id = decode_hashid(hashed_id)
        if subject_id is None:
            raise Http404("無效的科目ID")

        subject = get_object_or_404(Subject, pk=subject_id)

        # 獲取該科目的所有問題ID
        question_ids = list(Question.objects.filter(subject=subject).values_list('id', flat=True))

        # 檢查題目數量是否足夠
        if len(question_ids) < EXAM_QUESTIONS_COUNT:
            messages.error(self.request, _("抱歉，該科目的題目數量不足以開始一場模擬考試。"))
            return redirect('questions:subject_detail', hashed_id=hash_id(subject.id))

        # 隨機抽取題目
        random_question_ids = random.sample(question_ids, EXAM_QUESTIONS_COUNT)

        # 創建考試會話
        with transaction.atomic():
            exam_session = ExamSession.objects.create(
                user=self.request.user,
                subject=subject,
                questions_list=random_question_ids
            )

        # 重定向到考試頁面
        return redirect('exams:take_exam', hashed_id=hash_id(exam_session.id))

class TakeExamView(LoginRequiredMixin, View):
    """
    處理進行考試（GET）和提交試卷（POST）。
    """
    template_name = 'exams/take_exam.html'
    
    def get(self, request, *args, **kwargs):
        hashed_id = self.kwargs.get('hashed_id')
        session_id = decode_hashid(hashed_id)
        if session_id is None:
            raise Http404("無效的考試會話ID")

        exam_session = get_object_or_404(ExamSession, pk=session_id, user=request.user)
        
        if exam_session.is_completed:
             return redirect('exams:exam_result', hashed_id=hash_id(exam_session.id))

        # 這裡需要獲取問題列表並傳遞給模板
        questions = Question.objects.filter(id__in=exam_session.questions_list).order_by('?')
        
        context = {
            'exam_session': exam_session,
            'questions': questions
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        hashed_id = self.kwargs.get('hashed_id')
        session_id = decode_hashid(hashed_id)
        if session_id is None:
            raise Http404("無效的考試會話ID")

        exam_session = get_object_or_404(ExamSession, pk=session_id, user=request.user)

        if exam_session.is_completed:
            messages.warning(request, _("本次考試已提交，請勿重複提交。"))
            return redirect('exams:exam_result', hashed_id=hash_id(exam_session.id))

        questions = Question.objects.filter(id__in=exam_session.questions_list)
        user_answers = {}
        correct_count = 0

        # 從 POST 數據中提取用戶答案
        for question in questions:
            answer_key = f'question_{question.id}'
            user_answer = request.POST.get(answer_key)
            if user_answer:
                user_answers[str(question.id)] = user_answer
                if question.is_correct(user_answer):
                    correct_count += 1
        
        # 計算得分率
        total_questions = len(exam_session.questions_list)
        score = round((correct_count / total_questions) * 100, 2) if total_questions > 0 else 0

        with transaction.atomic():
            # 更新 ExamSession
            exam_session.complete_session(final_score=score, answers=user_answers)
            
            # 更新 UserProgress
            progress, _ = UserProgress.objects.get_or_create(
                user=request.user,
                subject=exam_session.subject
            )
            progress.update_score(new_score=score)

        messages.success(request, _("考試完成！查看您的成績報告。"))
        return redirect('exams:exam_result', hashed_id=hash_id(exam_session.id))


class ExamResultView(LoginRequiredMixin, DetailView):
    """
    顯示一場已完成考試的結果。
    """
    model = ExamSession
    template_name = 'exams/exam_result.html'
    context_object_name = 'exam_session'
    slug_field = 'hashed_id' 
    slug_url_kwarg = 'hashed_id'

    def get_object(self, queryset=None):
        hashed_id = self.kwargs.get('hashed_id')
        session_id = decode_hashid(hashed_id)
        if session_id is None:
            raise Http404("無效的考試會話ID")
        
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=session_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam_session = self.get_object()
        
        # 確保考試已經完成
        if not exam_session.is_completed:
            messages.warning(self.request, _("本次考試尚未完成。"))
            return redirect('exams:take_exam', hashed_id=self.kwargs.get('hashed_id'))

        # 獲取問題的詳細信息
        questions_dict = Question.objects.in_bulk(exam_session.questions_list)
        
        results = []
        for q_id_str in exam_session.questions_list:
            question = questions_dict.get(int(q_id_str))
            if not question: continue

            user_answer = exam_session.user_answers.get(str(question.id))
            
            results.append({
                'question': question,
                'user_answer': user_answer,
                'user_answer_display': question.get_answer_display(user_answer),
                'is_correct': question.is_correct(user_answer),
                'correct_answer_display': question.get_correct_answer_display(),
            })
            
        context['results'] = results
        return context

    def get_queryset(self):
        # 確保使用者只能看到自己的考試結果
        return super().get_queryset().filter(user=self.request.user)
