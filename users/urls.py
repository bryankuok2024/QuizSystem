from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('verify-signup-code/', views.verify_signup_code_view, name='account_verify_signup_code'),
    # 用戶相關 URLs 將在這裡添加
    path('profile/', views.profile, name='profile'),
    # path('profile/edit/', views.edit_profile_view, name='edit_profile'), # 暂时移除，因为视图函数缺失
    path('dashboard/', views.dashboard, name='dashboard'),
] 