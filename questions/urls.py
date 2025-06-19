from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    # URL for practicing a single question, using the hashed ID
    path('practice/<str:hashed_id>/', views.PracticeQuestionView.as_view(), name='practice_question'),
    
    # The practice_quiz_view now handles both GET (showing questions) and POST (submitting answers)
    path('practice-quiz/', views.practice_quiz_view, name='practice_quiz'),
    # This URL is now routed to the main practice_quiz_view, which handles the submission
    path('practice-quiz/submit/', views.practice_quiz_view, name='practice_quiz_submit'),
    path('practice-quiz/result/', views.practice_result_view, name='practice_result'),
    path('wrong-questions/', views.wrong_questions_practice_view, name='wrong_questions_practice'),

    # Example URLs for listing and detailing subjects (if you have them)
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<str:hashed_id>/', views.SubjectDetailView.as_view(), name='subject_detail'),

    # Search
    path('search/', views.question_search_view, name='question_search'),

    # AJAX endpoints
    path('bookmark/toggle/<str:hashed_id>/', views.toggle_bookmark_view, name='toggle_bookmark'),
    path('bookmarks/', views.bookmarks_list_view, name='bookmark_list'),
] 