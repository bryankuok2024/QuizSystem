#!/usr/bin/env python
"""
Celery 任務測試腳本
"""

import os
import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')
django.setup()

def test_celery_tasks():
    """測試 Celery 任務導入和配置"""
    print("🔍 測試 Celery 任務配置...")
    
    try:
        # 測試導入 Celery app
        from quizApp.celery import app as celery_app
        print(f"✅ Celery App 導入成功: {celery_app}")
        
        # 測試導入各個應用的任務
        print("\n📋 導入任務模塊:")
        
        # 用戶任務
        try:
            from users.tasks import send_welcome_email, send_password_reset_email
            print("✅ users.tasks - 歡迎郵件、密碼重置郵件")
        except Exception as e:
            print(f"❌ users.tasks 導入失敗: {e}")
        
        # 題目任務
        try:
            from questions.tasks import (
                batch_import_questions, 
                generate_question_statistics, 
                cleanup_draft_questions
            )
            print("✅ questions.tasks - 批量導入、統計生成、草稿清理")
        except Exception as e:
            print(f"❌ questions.tasks 導入失敗: {e}")
        
        # 支付任務
        try:
            from payments.tasks import (
                process_payment_confirmation,
                generate_qr_code,
                check_subscription_status,
                send_payment_reminder
            )
            print("✅ payments.tasks - 支付確認、二維碼生成、訂閱檢查、支付提醒")
        except Exception as e:
            print(f"❌ payments.tasks 導入失敗: {e}")
        
        # 進度任務
        try:
            from progress.tasks import (
                calculate_user_progress,
                generate_progress_report,
                update_user_rankings,
                send_study_reminder
            )
            print("✅ progress.tasks - 進度計算、報告生成、排名更新、學習提醒")
        except Exception as e:
            print(f"❌ progress.tasks 導入失敗: {e}")
        
        # 檢查 Celery 配置
        print(f"\n📊 Celery 配置信息:")
        print(f"   Broker URL: {celery_app.conf.broker_url}")
        print(f"   Result Backend: {celery_app.conf.result_backend}")
        print(f"   Task Serializer: {celery_app.conf.task_serializer}")
        print(f"   Result Serializer: {celery_app.conf.result_serializer}")
        print(f"   Timezone: {celery_app.conf.timezone}")
        
        # 列出所有註冊的任務
        print(f"\n📝 已註冊的任務:")
        for task_name in sorted(celery_app.tasks.keys()):
            if not task_name.startswith('celery.'):
                print(f"   - {task_name}")
        
        print("\n✅ Celery 任務配置測試完成！")
        return True
        
    except Exception as e:
        print(f"❌ Celery 任務測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 Celery 任務測試開始...")
    print("=" * 50)
    
    success = test_celery_tasks()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Celery 任務測試成功！")
        print("\n📝 啟動 Celery Worker:")
        print("   celery -A quizApp worker --loglevel=info --pool=solo")
        print("\n📝 啟動 Celery Beat (定時任務):")
        print("   celery -A quizApp beat --loglevel=info")
        print("\n💡 提示:")
        print("   - 確保 Redis 服務器正在運行")
        print("   - Windows 環境下使用 --pool=solo 參數")
        print("   - 可以在不同終端窗口中分別啟動 worker 和 beat")
    else:
        print("❌ Celery 任務測試失敗！")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 