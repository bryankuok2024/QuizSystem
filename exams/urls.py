from django.urls import path
from . import views

app_name = 'exams'
 
urlpatterns = [
    path('start/<int:subject_pk>/', views.StartExamView.as_view(), name='start_exam'),
    path('take/<int:session_pk>/', views.TakeExamView.as_view(), name='take_exam'),
    path('result/<int:session_pk>/', views.ExamResultView.as_view(), name='exam_result'),
] 