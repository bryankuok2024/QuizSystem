#!/usr/bin/env python
"""
Gmail SMTP 配置測試腳本
專門測試由 Gmail 託管的 yenoo.co 域名郵件服務
"""
import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from django.core.mail import send_mail

def test_gmail_smtp_config():
    """測試 Gmail SMTP 配置"""
    print("📧 Gmail SMTP 配置測試")
    print("=" * 60)
    
    # 檢查環境變數
    email_user = os.getenv('EMAIL_HOST_USER', '')
    email_password = os.getenv('EMAIL_HOST_PASSWORD', '')
    use_smtp = os.getenv('USE_GMAIL_SMTP', 'False')
    
    print("📋 環境變數檢查:")
    print(f"   📧 郵件地址: {email_user}")
    print(f"   🔑 密碼: {'已設置' if email_password else '未設置'}")
    print(f"   🔧 SMTP 啟用: {use_smtp}")
    
    # 確認是 yenoo.co 域名
    if '@yenoo.co' in email_user:
        print("   🏢 確認為 Yenoo 自定義域名（由 Gmail 託管）")
    elif '@gmail.com' in email_user:
        print("   🏢 確認為 Gmail 地址")
    else:
        print("   ⚠️  未知的郵件域名")
    
    print(f"\n📧 Django 郵件設置:")
    print(f"   後端: {settings.EMAIL_BACKEND}")
    
    if hasattr(settings, 'EMAIL_HOST'):
        print(f"   SMTP 主機: {settings.EMAIL_HOST}")
        print(f"   SMTP 端口: {settings.EMAIL_PORT}")
        print(f"   TLS 加密: {getattr(settings, 'EMAIL_USE_TLS', False)}")
        print(f"   SSL 加密: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    
    print(f"   寄件人: {settings.DEFAULT_FROM_EMAIL}")
    
    # 檢查是否正確配置為 Gmail SMTP
    if (settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend' 
        and hasattr(settings, 'EMAIL_HOST') 
        and settings.EMAIL_HOST == 'smtp.gmail.com'):
        print("\n✅ Gmail SMTP 配置正確！")
        return True
    else:
        print("\n❌ Gmail SMTP 配置有問題")
        return False

def send_test_email():
    """發送測試郵件"""
    if settings.EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
        print("\n⚠️  跳過郵件發送測試（SMTP 未啟用）")
        return True
    
    print(f"\n📮 Gmail SMTP 郵件發送測試")
    print("-" * 40)
    
    # 使用寄件人自己的郵箱進行測試
    test_email = os.getenv('EMAIL_HOST_USER', '')
    if not test_email:
        print("❌ 無法獲取測試郵件地址")
        return False
    
    print(f"📬 測試郵件將發送到: {test_email}")
    
    try:
        # 發送測試郵件
        result = send_mail(
            subject='[題庫系統] Gmail SMTP 配置測試成功',
            message=f'''恭喜！Gmail SMTP 配置測試成功！

配置詳情:
- 寄件人: {settings.DEFAULT_FROM_EMAIL}
- SMTP 主機: {getattr(settings, 'EMAIL_HOST', '未設置')}
- 端口: {getattr(settings, 'EMAIL_PORT', '未設置')}
- TLS 加密: {getattr(settings, 'EMAIL_USE_TLS', False)}
- 郵件地址: {test_email}

這表示您的 Django 項目已成功配置 Gmail SMTP 服務！

現在您可以：
1. 測試用戶註冊和郵件驗證
2. 測試密碼重置功能
3. 使用 django-allauth 的完整功能

題庫系統開發團隊
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result == 1:
            print("🎉 測試郵件發送成功！")
            print(f"📬 請檢查 {test_email} 的收件箱")
            print("   （可能在垃圾郵件資料夾中）")
            return True
        else:
            print("❌ 郵件發送失敗（無明確錯誤）")
            return False
            
    except Exception as e:
        print(f"❌ 郵件發送錯誤: {e}")
        print("\n🔧 可能的解決方案:")
        
        if 'authentication' in str(e).lower():
            print("   認證錯誤 - 請檢查:")
            print("   1. 郵件地址和密碼是否正確")
            print("   2. 如果是 Gmail，是否需要應用程式密碼")
            print("   3. 是否啟用了兩步驟驗證")
        elif 'connection' in str(e).lower():
            print("   連接錯誤 - 請檢查:")
            print("   1. 網路連接是否正常")
            print("   2. 防火牆是否阻擋 SMTP 連接")
            print("   3. SMTP 設置是否正確")
        else:
            print("   其他錯誤 - 請檢查:")
            print("   1. Gmail 帳戶設置")
            print("   2. 應用程式密碼配置")
            print("   3. 兩步驟驗證設置")
        
        return False

def main():
    """主函數"""
    print("🚀 Gmail SMTP 配置完整測試")
    print("=" * 60)
    
    success = True
    
    # 測試基本配置
    if not test_gmail_smtp_config():
        success = False
    
    # 測試發送郵件
    if not send_test_email():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Gmail SMTP 配置測試完全成功！")
        print("\n📋 接下來您可以:")
        print("1. 重新啟動 Django 開發服務器")
        print("2. 訪問註冊頁面: http://127.0.0.1:8000/accounts/signup/")
        print("3. 測試完整的註冊和郵件驗證流程")
        print("4. 測試密碼重置功能")
    else:
        print("❌ 部分測試失敗")
        print("\n📋 建議檢查:")
        print("1. Gmail 帳戶是否啟用了應用程式密碼")
        print("2. 兩步驟驗證是否正確配置")
        print("3. 網路連接是否正常")
    
    print(f"\n💡 當前配置:")
    print(f"   📧 郵件: {os.getenv('EMAIL_HOST_USER', '未設置')}")
    print(f"   🏢 服務: Yenoo 自定義域名（由 Gmail 託管）")
    print(f"   🔧 SMTP: smtp.gmail.com:587 (TLS)")

if __name__ == '__main__':
    main() 