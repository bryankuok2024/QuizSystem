#!/usr/bin/env python
"""
Gmail SMTP 配置測試腳本
"""
import os
import sys
import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import smtplib

def test_email_settings():
    """測試郵件設置"""
    print("📧 Gmail SMTP 配置測試")
    print("=" * 50)
    
    # 檢查設置
    print(f"郵件後端: {settings.EMAIL_BACKEND}")
    
    if hasattr(settings, 'EMAIL_HOST'):
        print(f"SMTP 主機: {settings.EMAIL_HOST}")
        print(f"SMTP 端口: {settings.EMAIL_PORT}")
        print(f"TLS 啟用: {getattr(settings, 'EMAIL_USE_TLS', False)}")
        print(f"SSL 啟用: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        print(f"寄件人: {settings.DEFAULT_FROM_EMAIL}")
        print(f"主機用戶: {getattr(settings, 'EMAIL_HOST_USER', '未設置')}")
        print(f"密碼: {'已設置' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else '未設置'}")
    
    print("\n" + "=" * 50)
    
    # 檢查是否使用 Gmail SMTP
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
        return test_smtp_connection()
    else:
        print("ℹ️ 目前使用控制台郵件後端")
        print("📝 若要測試 Gmail SMTP，請:")
        print("1. 創建 .env 文件")
        print("2. 設置 USE_GMAIL_SMTP=True")
        print("3. 添加您的 Gmail 憑證")
        return True

def test_smtp_connection():
    """測試 SMTP 連接"""
    print("🔍 測試 SMTP 連接...")
    
    try:
        # 測試連接
        from django.core.mail import get_connection
        connection = get_connection()
        connection.open()
        
        print("✅ SMTP 連接成功")
        connection.close()
        
        return test_send_email()
        
    except Exception as e:
        print(f"❌ SMTP 連接失敗: {e}")
        print("\n🔧 可能的解決方案:")
        print("1. 檢查 Gmail 應用程式密碼是否正確")
        print("2. 確認 2 步驟驗證已啟用")
        print("3. 檢查網路連接")
        return False

def test_send_email():
    """測試發送郵件"""
    print("\n📮 測試發送郵件...")
    
    # 請用戶輸入測試郵件地址
    test_email = input("請輸入測試郵件地址 (按 Enter 跳過): ").strip()
    
    if not test_email:
        print("⏭️ 跳過郵件發送測試")
        return True
    
    try:
        # 發送測試郵件
        result = send_mail(
            subject='[題庫系統] Gmail SMTP 測試郵件',
            message='這是一封來自題庫系統的測試郵件。\n\n如果您收到此郵件，表示 Gmail SMTP 配置成功！',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ 測試郵件發送成功")
            print(f"📬 請檢查 {test_email} 的收件箱")
            return True
        else:
            print("❌ 郵件發送失敗")
            return False
            
    except Exception as e:
        print(f"❌ 郵件發送錯誤: {e}")
        return False

def test_allauth_email():
    """測試 allauth 郵件配置"""
    print("\n🔐 測試 allauth 郵件配置...")
    
    # 檢查 allauth 設置
    print(f"郵件驗證: {getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', '未設置')}")
    print(f"郵件必填: {getattr(settings, 'ACCOUNT_EMAIL_REQUIRED', False)}")
    print(f"唯一郵件: {getattr(settings, 'ACCOUNT_UNIQUE_EMAIL', False)}")
    print(f"郵件主題前綴: {getattr(settings, 'EMAIL_SUBJECT_PREFIX', '未設置')}")
    
    if getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', '') == 'mandatory':
        print("✅ 強制郵件驗證已啟用")
    else:
        print("⚠️ 建議啟用強制郵件驗證")
    
    return True

def main():
    """主函數"""
    try:
        success = True
        
        # 測試基本設置
        if not test_email_settings():
            success = False
        
        # 測試 allauth 配置
        if not test_allauth_email():
            success = False
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Gmail SMTP 配置測試完成")
            print("\n📋 下一步:")
            print("1. 訪問註冊頁面測試郵件驗證")
            print("2. 訪問密碼重置頁面測試重置郵件")
            print("3. 檢查郵件是否正常發送和接收")
        else:
            print("❌ 部分測試失敗，請檢查配置")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 測試已中斷")
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {e}")

if __name__ == '__main__':
    main() 