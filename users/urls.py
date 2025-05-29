from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('verify-signup-code/', views.verify_signup_code_view, name='account_verify_signup_code'),
    # 用戶相關 URLs 將在這裡添加
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
] 