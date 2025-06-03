from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('add/', views.add_question_view, name='add_question'),
    # Add other question-related URLs here as needed
] 