from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('add/', views.add_question_view, name='add_question'),
    path('practice/', views.practice_quiz_view, name='practice_quiz'),
    path('<int:question_pk>/practice/', views.PracticeQuestionView.as_view(), name='practice_question'),
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    # Add other question-related URLs here as needed
] 