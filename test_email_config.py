#!/usr/bin/env python
"""
郵件配置測試腳本
"""
import os
import sys

# 先載入環境變數
from dotenv import load_dotenv
load_dotenv()

import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from django.core.mail import send_mail

def test_email_config():
    """測試郵件配置"""
    print("📧 郵件配置測試")
    print("=" * 50)
    
    # 重新載入環境變數以確保正確讀取
    from dotenv import load_dotenv
    load_dotenv()
    
    # 檢查環境變數
    env_vars = {
        'USE_GMAIL_SMTP': os.getenv('USE_GMAIL_SMTP'),
        'EMAIL_HOST_USER': os.getenv('EMAIL_HOST_USER'),
        'EMAIL_HOST_PASSWORD': '已設置' if os.getenv('EMAIL_HOST_PASSWORD') else '未設置',
        'DEFAULT_FROM_EMAIL': os.getenv('DEFAULT_FROM_EMAIL')
    }
    
    print("📋 環境變數:")
    for key, value in env_vars.items():
        print(f"  {key}: {value}")
    
    print(f"\n📧 Django 郵件設置:")
    print(f"  後端: {settings.EMAIL_BACKEND}")
    
    if hasattr(settings, 'EMAIL_HOST'):
        print(f"  主機: {settings.EMAIL_HOST}")
        print(f"  端口: {settings.EMAIL_PORT}")
        print(f"  TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
        print(f"  SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    
    print(f"  寄件人: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  主題前綴: {getattr(settings, 'EMAIL_SUBJECT_PREFIX', '未設置')}")
    
    print("\n" + "=" * 50)
    
    # 檢查是否啟用 SMTP
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
        print("✅ SMTP 郵件後端已啟用")
        
        # 檢測郵件服務商
        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        if '@gmail.com' in email_user:
            print("🔍 檢測到 Gmail 服務")
        elif '@yenoo.co' in email_user:
            print("🔍 檢測到 Yenoo 自定義域名服務")
        else:
            print("🔍 檢測到其他郵件服務")
        
        return True
    else:
        print("ℹ️ 目前使用控制台後端（開發模式）")
        print("\n❗ 注意：環境變數可能未正確載入，請檢查：")
        print("1. .env 文件位置是否正確")
        print("2. USE_GMAIL_SMTP 是否設為 True")
        print("3. 重新啟動 Django 開發服務器")
        return False

def test_send_email():
    """測試發送郵件"""
    if settings.EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
        print("⏭️ 跳過實際郵件發送測試（未啟用 SMTP）")
        return True
    
    print("\n📮 測試發送郵件...")
    
    # 請用戶輸入測試郵件地址
    test_email = input("請輸入測試郵件地址 (按 Enter 跳過): ").strip()
    
    if not test_email:
        print("⏭️ 跳過郵件發送測試")
        return True
    
    try:
        # 發送測試郵件
        result = send_mail(
            subject='[題庫系統] 郵件設定測試',
            message=f'''這是一封來自題庫系統的測試郵件。

配置資訊:
- 寄件人: {settings.DEFAULT_FROM_EMAIL}
- SMTP 主機: {getattr(settings, 'EMAIL_HOST', '未設置')}
- TLS 加密: {getattr(settings, 'EMAIL_USE_TLS', False)}

如果您收到此郵件，表示郵件 SMTP 配置成功！

題庫系統團隊
''',
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
        print("\n🔧 可能的解決方案:")
        print("1. 檢查郵件帳號和密碼是否正確")
        print("2. 確認 SMTP 主機設置正確")
        print("3. 檢查網路連接")
        print("4. 如果是企業郵箱，可能需要聯繫 IT 部門確認 SMTP 設置")
        return False

def main():
    """主函數"""
    print("🚀 郵件配置測試")
    print("=" * 50)
    
    success = True
    
    # 測試基本配置
    if not test_email_config():
        success = False
    
    # 測試發送郵件
    if not test_send_email():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 郵件配置測試完成！")
        print("\n📋 下一步:")
        print("1. 重新啟動 Django 開發服務器")
        print("2. 訪問註冊頁面: http://127.0.0.1:8000/accounts/signup/")
        print("3. 測試註冊流程和郵件驗證")
        print("4. 測試密碼重置功能")
    else:
        print("❌ 部分測試失敗，請檢查配置")
    
    print(f"\n💡 目前配置:")
    print(f"   郵件: {os.getenv('EMAIL_HOST_USER', '未設置')}")
    print(f"   域名: {'@yenoo.co (自定義域名)' if '@yenoo.co' in os.getenv('EMAIL_HOST_USER', '') else 'Gmail 或其他'}")

if __name__ == '__main__':
    main() 