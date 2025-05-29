#!/usr/bin/env python
"""
Django-allauth 配置測試腳本
"""
import os
import sys
import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from django.test.utils import get_runner
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

def test_allauth_configuration():
    """測試 django-allauth 配置"""
    print("🔧 測試 Django-allauth 配置...")
    
    # 檢查必要的設置
    required_settings = [
        'ACCOUNT_EMAIL_VERIFICATION',
        'ACCOUNT_UNIQUE_EMAIL',
        'LOGIN_URL',
        'LOGIN_REDIRECT_URL',
        'LOGOUT_REDIRECT_URL',
    ]
    
    for setting in required_settings:
        if hasattr(settings, setting):
            value = getattr(settings, setting)
            print(f"✅ {setting}: {value}")
        else:
            print(f"❌ 缺少設置: {setting}")
    
    # 檢查 INSTALLED_APPS
    required_apps = [
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
    ]
    
    print("\n📦 檢查已安裝的應用...")
    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print(f"✅ {app}")
        else:
            print(f"❌ 缺少應用: {app}")
    
    # 檢查 AUTHENTICATION_BACKENDS
    print("\n🔐 檢查認證後端...")
    required_backends = [
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    ]
    
    for backend in required_backends:
        if backend in settings.AUTHENTICATION_BACKENDS:
            print(f"✅ {backend}")
        else:
            print(f"❌ 缺少認證後端: {backend}")
    
    # 檢查 MIDDLEWARE
    print("\n🔗 檢查中間件...")
    required_middleware = [
        'allauth.account.middleware.AccountMiddleware',
    ]
    
    for middleware in required_middleware:
        if middleware in settings.MIDDLEWARE:
            print(f"✅ {middleware}")
        else:
            print(f"❌ 缺少中間件: {middleware}")
    
    print("\n✨ Django-allauth 配置檢查完成！")

def test_database_connection():
    """測試數據庫連接"""
    print("\n🗄️  測試數據庫連接...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print("✅ 數據庫連接成功")
            
            # 檢查 allauth 相關表
            cursor.execute("SHOW TABLES LIKE 'account_%'")
            tables = cursor.fetchall()
            print(f"✅ 找到 {len(tables)} 個 allauth 相關表")
            
    except Exception as e:
        print(f"❌ 數據庫連接失敗: {e}")

def test_user_model():
    """測試用戶模型"""
    print("\n👤 測試用戶模型...")
    
    try:
        User = get_user_model()
        print(f"✅ 用戶模型: {User}")
        
        # 檢查是否有用戶
        user_count = User.objects.count()
        print(f"✅ 用戶總數: {user_count}")
        
        # 檢查 EmailAddress 模型
        email_count = EmailAddress.objects.count()
        print(f"✅ 郵件地址總數: {email_count}")
        
    except Exception as e:
        print(f"❌ 用戶模型測試失敗: {e}")

def main():
    """主函數"""
    print("🚀 開始測試 Django-allauth 配置...")
    print("=" * 50)
    
    test_allauth_configuration()
    test_database_connection()
    test_user_model()
    
    print("\n" + "=" * 50)
    print("🎉 測試完成！")
    print("\n📝 使用說明:")
    print("1. 啟動開發服務器: python manage.py runserver")
    print("2. 訪問主頁: http://127.0.0.1:8000/")
    print("3. 註冊新用戶: http://127.0.0.1:8000/accounts/signup/")
    print("4. 登入: http://127.0.0.1:8000/accounts/login/")
    print("5. 管理後台: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    main() 