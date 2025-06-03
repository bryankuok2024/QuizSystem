from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import QuestionForm
from .models import Question
import hashlib
import json

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

# def add_question_view(request):
#     return HttpResponse("This is a placeholder for add_question_view in quizApp/questions.") 