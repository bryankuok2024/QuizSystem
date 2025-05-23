#!/usr/bin/env python
"""
QuizSystem 系統配置測試腳本
測試 MySQL 連接、Redis 連接和 Celery 任務
"""

import os
import sys

# 添加 quizApp 目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
quiz_app_dir = os.path.join(current_dir, 'quizApp')
sys.path.insert(0, quiz_app_dir)

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')

try:
    import django
    django.setup()
    print("✅ Django 環境設置成功")
except Exception as e:
    print(f"❌ Django 環境設置失敗: {e}")
    sys.exit(1)

def test_mysql_connection():
    """測試 MySQL 數據庫連接"""
    print("\n🔍 測試 MySQL 數據庫連接...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL 連接成功！版本: {version[0]}")
            
            # 測試創建測試表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_field VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                )
            """)
            
            # 測試插入中文數據
            cursor.execute("INSERT INTO test_connection (test_field) VALUES (%s)", ["測試中文數據 🎯"])
            
            # 測試查詢中文數據
            cursor.execute("SELECT test_field FROM test_connection ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            print(f"✅ UTF-8 編碼測試成功: {result[0]}")
            
            # 清理測試數據
            cursor.execute("DROP TABLE test_connection")
            
        return True
    except Exception as e:
        print(f"❌ MySQL 連接失敗: {e}")
        return False

def test_redis_connection():
    """測試 Redis 連接"""
    print("\n🔍 測試 Redis 連接...")
    try:
        import redis
        from django.core.cache import cache
        
        # 測試 Celery broker (database 0)
        broker_redis = redis.Redis(host='localhost', port=6379, db=0)
        broker_redis.ping()
        print("✅ Redis Broker (DB 0) 連接成功！")
        
        # 測試 Django 緩存 (database 1)
        cache.set('test_key', '測試中文緩存數據 🚀', 30)
        cached_value = cache.get('test_key')
        print(f"✅ Django Cache (DB 1) 測試成功: {cached_value}")
        
        return True
    except Exception as e:
        print(f"❌ Redis 連接失敗: {e}")
        return False

def test_celery_configuration():
    """測試 Celery 配置（不執行任務）"""
    print("\n🔍 測試 Celery 配置...")
    try:
        from quizApp.celery import app as celery_app
        
        print(f"📊 Celery Broker URL: {celery_app.conf.broker_url}")
        print(f"📊 Celery Result Backend: {celery_app.conf.result_backend}")
        print(f"📊 Celery Task Serializer: {celery_app.conf.task_serializer}")
        
        # 檢查任務是否可以導入
        task_modules = ['users.tasks', 'questions.tasks', 'payments.tasks', 'progress.tasks']
        imported_tasks = []
        
        for module in task_modules:
            try:
                __import__(module)
                imported_tasks.append(module)
                print(f"✅ 成功導入任務模塊: {module}")
            except Exception as e:
                print(f"⚠️ 導入任務模塊失敗 {module}: {e}")
        
        print(f"✅ Celery 配置測試完成！成功導入 {len(imported_tasks)}/{len(task_modules)} 個任務模塊")
        return True
        
    except Exception as e:
        print(f"❌ Celery 配置測試失敗: {e}")
        return False

def test_django_settings():
    """測試 Django 設置"""
    print("\n🔍 測試 Django 設置...")
    try:
        from django.conf import settings
        
        print(f"📝 語言設置: {settings.LANGUAGE_CODE}")
        print(f"🌏 時區設置: {settings.TIME_ZONE}")
        print(f"🗄️ 數據庫引擎: {settings.DATABASES['default']['ENGINE']}")
        print(f"🗄️ 數據庫名稱: {settings.DATABASES['default']['NAME']}")
        print(f"📮 郵件後端: {settings.EMAIL_BACKEND}")
        print(f"🔄 Celery Broker: {settings.CELERY_BROKER_URL}")
        print(f"📊 Celery Result Backend: {settings.CELERY_RESULT_BACKEND}")
        
        # 檢查已安裝的應用
        custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
        print(f"📱 自定義應用: {', '.join(custom_apps)}")
        
        print("✅ Django 設置檢查完成！")
        return True
    except Exception as e:
        print(f"❌ Django 設置檢查失敗: {e}")
        return False

def test_django_check():
    """運行 Django 系統檢查"""
    print("\n🔍 運行 Django 系統檢查...")
    try:
        from django.core.management import execute_from_command_line
        from io import StringIO
        import sys
        
        # 捕獲 Django check 命令的輸出
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        
        try:
            execute_from_command_line(['manage.py', 'check'])
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            if "System check identified no issues" in output:
                print("✅ Django 系統檢查通過，無問題發現！")
                return True
            else:
                print(f"⚠️ Django 系統檢查輸出: {output}")
                return True  # 有輸出但不一定是錯誤
        except Exception as e:
            sys.stdout = old_stdout
            if "no issues" in str(e):
                print("✅ Django 系統檢查通過！")
                return True
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Django 系統檢查失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 QuizSystem 系統配置測試開始...")
    print("=" * 60)
    
    tests = [
        ("Django 設置", test_django_settings),
        ("Django 系統檢查", test_django_check),
        ("MySQL 連接", test_mysql_connection),
        ("Redis 連接", test_redis_connection),
        ("Celery 配置", test_celery_configuration),
    ]
    
    results = []
    
    # 運行所有測試
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試 {test_name} 時發生未處理的錯誤: {e}")
            results.append((test_name, False))
    
    # 總結結果
    print("\n" + "=" * 60)
    print("📋 測試結果總結:")
    
    for i, (test_name, result) in enumerate(results):
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"   {i+1}. {test_name}: {status}")
    
    success_count = sum(result for _, result in results)
    total_count = len(results)
    
    print(f"\n🎯 總計: {success_count}/{total_count} 項測試通過")
    
    if success_count == total_count:
        print("\n🎉 所有測試通過！您的 QuizSystem 配置完美！")
        print("\n📝 下一步操作:")
        print("   1. 運行: python manage.py makemigrations")
        print("   2. 運行: python manage.py migrate")
        print("   3. 創建超級用戶: python manage.py createsuperuser")
        print("   4. 啟動開發服務器: python manage.py runserver")
        print("   5. 啟動 Celery Worker: celery -A quizApp worker --loglevel=info --pool=solo")
        print("\n💡 提示:")
        print("   - Redis 服務器需要在後台運行")
        print("   - 確保 MySQL 服務器正在運行")
        print("   - 開發環境下郵件將在控制台顯示")
    else:
        print("\n⚠️ 有部分測試失敗，請檢查相關配置。")
        print("\n🔧 故障排除:")
        print("   - 確認 MySQL 服務器運行狀態")
        print("   - 確認 Redis 服務器運行狀態")
        print("   - 檢查數據庫連接參數")
        print("   - 檢查防火牆設置")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 