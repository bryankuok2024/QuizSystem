from django.urls import path
from . import views

app_name = 'exams'
 
urlpatterns = [
    path('start/<str:hashed_id>/', views.StartExamView.as_view(), name='start_exam'),
    path('take/<str:hashed_id>/', views.TakeExamView.as_view(), name='take_exam'),
    path('result/<str:hashed_id>/', views.ExamResultView.as_view(), name='exam_result'),
] 