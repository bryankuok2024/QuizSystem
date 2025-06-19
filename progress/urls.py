from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('report/', views.progress_report_view, name='report'),
    path('api/all-subjects-progress/', views.all_subjects_progress_api, name='api_all_subjects_progress'),
] 