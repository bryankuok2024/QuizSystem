from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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