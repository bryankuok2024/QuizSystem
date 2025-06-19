from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserProgress, UserAnswerLog
from questions.models import Subject
from exams.models import ExamSession
from django.db.models import Sum, Count, Max, Avg, Q
from django.utils import timezone
from datetime import date, timedelta
import json
from django.contrib import messages

# Create your views here.

@login_required
def progress_overview(request):
    """進度總覽頁面"""
    return render(request, 'progress/progress_overview.html')

@login_required
def progress_reports(request):
    """進度報告頁面"""
    return render(request, 'progress/progress_reports.html')

@login_required
def user_rankings(request):
    """用戶排名頁面"""
    return render(request, 'progress/user_rankings.html')

@login_required
def progress_report_view(request):
    """
    為使用者生成一份全面的學習進度報告。
    """
    user = request.user
    progress_records = UserProgress.objects.filter(user=user).select_related('subject')
    
    report_data = []

    # 獲取所有相關的模擬考試數據以提高效率
    subject_ids = progress_records.values_list('subject_id', flat=True)
    all_exam_sessions = ExamSession.objects.filter(
        user=user, 
        subject_id__in=subject_ids, 
        is_completed=True
    )
    
    exam_stats_map = {}
    for session in all_exam_sessions:
        if session.subject_id not in exam_stats_map:
            exam_stats_map[session.subject_id] = {'sessions': []}
        exam_stats_map[session.subject_id]['sessions'].append(session)

    for subject_id, stats in exam_stats_map.items():
        scores = [s.score for s in stats['sessions']]
        stats['num_exams'] = len(scores)
        stats['avg_exam_score'] = sum(scores) / len(scores) if scores else 0.0
        stats['highest_exam_score'] = max(scores) if scores else 0.0

    for progress in progress_records:
        # 只有當一個科目既沒有練習記錄，也沒有考試記錄時，才跳過它
        exam_stats = exam_stats_map.get(progress.subject.id, {})
        num_exams = exam_stats.get('num_exams', 0)

        if progress.total_questions_answered == 0 and num_exams == 0:
            continue

        report_data.append({
            'subject_name': progress.subject.name,
            'total_answered_practice': progress.total_questions_answered,
            'practice_accuracy': round(progress.overall_accuracy(), 2),
            'num_exams': num_exams,
            'avg_exam_score': round(exam_stats.get('avg_exam_score', 0.0), 2),
            'highest_exam_score': round(exam_stats.get('highest_exam_score', 0.0), 2),
        })

    # Note: Consecutive days and last practice date logic is removed for simplification,
    # as it requires more complex cross-model queries. This can be added back later if needed.

    context = {
        'report_data': report_data,
        'report_data_json': json.dumps(report_data),
        'has_data': bool(report_data)
    }
    
    return render(request, 'progress/report.html', context)

@login_required
def all_subjects_progress_api(request):
    """
    一個API端點，返回當前使用者所有科目的學習進度。
    數據格式: { subject_id: { answered: X, total: Y }, ... }
    """
    user = request.user
    progress_records = UserProgress.objects.filter(user=user).select_related('subject')
    
    # 同時獲取所有相關科目的總題數以提高效率
    subject_ids = progress_records.values_list('subject_id', flat=True)
    question_counts = Subject.objects.filter(id__in=subject_ids).annotate(
        total_questions=Count('questions')
    ).values('id', 'total_questions')
    
    question_count_map = {item['id']: item['total_questions'] for item in question_counts}
    
    data = {}
    for progress in progress_records:
        subject_id = progress.subject.id
        data[subject_id] = {
            'answered': progress.total_questions_answered,
            'total': question_count_map.get(subject_id, 0)
        }
        
    return JsonResponse(data)

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj) 