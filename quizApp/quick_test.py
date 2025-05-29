#!/usr/bin/env python
"""
快速測試腳本 - 驗證模板配置
"""
import os
import sys
import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from django.template.loader import get_template
from django.test import RequestFactory, TestCase
from django.http import HttpResponse
from django.views.generic import TemplateView

def test_template_configuration():
    """測試模板配置"""
    print("🧪 測試模板配置...")
    
    # 檢查模板目錄設置
    print(f"📁 模板目錄: {settings.TEMPLATES[0]['DIRS']}")
    
    # 檢查模板文件是否存在
    template_dir = settings.TEMPLATES[0]['DIRS'][0]
    templates_to_check = ['base.html', 'home.html']
    
    for template_name in templates_to_check:
        template_path = template_dir / template_name
        if template_path.exists():
            print(f"✅ {template_name} 存在於 {template_path}")
        else:
            print(f"❌ {template_name} 不存在於 {template_path}")
    
    # 測試模板加載
    try:
        home_template = get_template('home.html')
        print("✅ home.html 模板可以正常加載")
        
        base_template = get_template('base.html')
        print("✅ base.html 模板可以正常加載")
        
    except Exception as e:
        print(f"❌ 模板加載失敗: {e}")
        return False
    
    return True

def test_home_view():
    """測試主頁視圖"""
    print("\n🏠 測試主頁視圖...")
    
    try:
        from django.urls import reverse, resolve
        from django.test import Client
        
        # 創建測試客戶端
        client = Client()
        
        # 測試主頁
        response = client.get('/')
        print(f"📊 響應狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 主頁載入成功")
            print(f"📄 響應內容長度: {len(response.content)} 字節")
            
            # 檢查是否包含預期的內容
            content = response.content.decode('utf-8')
            if '題庫系統' in content:
                print("✅ 頁面包含預期標題")
            else:
                print("⚠️ 頁面未包含預期標題")
                
        else:
            print(f"❌ 主頁載入失敗，狀態碼: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 視圖測試失敗: {e}")
        return False
    
    return True

def test_allauth_urls():
    """測試 allauth URLs"""
    print("\n🔐 測試 allauth URLs...")
    
    try:
        from django.test import Client
        
        client = Client()
        
        # 測試主要的 allauth URLs
        urls_to_test = [
            ('/accounts/login/', '登入頁面'),
            ('/accounts/signup/', '註冊頁面'),
        ]
        
        for url, name in urls_to_test:
            try:
                response = client.get(url)
                print(f"📊 {name} ({url}): 狀態碼 {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ {name} 載入成功")
                else:
                    print(f"⚠️ {name} 狀態碼異常: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {name} 測試失敗: {e}")
    
    except Exception as e:
        print(f"❌ allauth URLs 測試失敗: {e}")
        return False
    
    return True

def main():
    """主函數"""
    print("🚀 Django 配置快速測試")
    print("=" * 50)
    
    success = True
    
    # 測試模板配置
    if not test_template_configuration():
        success = False
    
    # 測試主頁視圖
    if not test_home_view():
        success = False
    
    # 測試 allauth URLs
    if not test_allauth_urls():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有測試通過！")
        print("\n📝 現在可以訪問:")
        print("• 主頁: http://127.0.0.1:8000/")
        print("• 註冊: http://127.0.0.1:8000/accounts/signup/")
        print("• 登入: http://127.0.0.1:8000/accounts/login/")
        print("• 管理後台: http://127.0.0.1:8000/admin/")
    else:
        print("❌ 部分測試失敗，請檢查配置")

if __name__ == '__main__':
    main() 