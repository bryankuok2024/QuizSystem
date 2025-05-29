from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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