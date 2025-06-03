#!/usr/bin/env python
"""
Celery 測試腳本
用於驗證 Celery 配置是否正常工作
"""

import os
import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizApp.settings')
django.setup()

from users.tasks import send_welcome_email
from questions.tasks import generate_question_statistics
from payments.tasks import generate_qr_code
from progress.tasks import calculate_user_progress

def test_celery_tasks():
    """測試所有 Celery 任務"""
    print("開始測試 Celery 任務...")
    
    # 測試用戶任務
    print("\n1. 測試用戶歡迎郵件任務...")
    try:
        result = send_welcome_email.delay("test@example.com", "測試用戶")
        print(f"任務已提交，任務 ID: {result.id}")
        print(f"任務狀態: {result.status}")
    except Exception as e:
        print(f"任務失敗: {e}")
    
    # 測試題目統計任務
    print("\n2. 測試題目統計任務...")
    try:
        result = generate_question_statistics.delay()
        print(f"任務已提交，任務 ID: {result.id}")
        print(f"任務狀態: {result.status}")
    except Exception as e:
        print(f"任務失敗: {e}")
    
    # 測試支付二維碼任務
    print("\n3. 測試支付二維碼生成任務...")
    try:
        result = generate_qr_code.delay("PAY12345", 99.99)
        print(f"任務已提交，任務 ID: {result.id}")
        print(f"任務狀態: {result.status}")
    except Exception as e:
        print(f"任務失敗: {e}")
    
    # 測試進度計算任務
    print("\n4. 測試用戶進度計算任務...")
    try:
        result = calculate_user_progress.delay(1)
        print(f"任務已提交，任務 ID: {result.id}")
        print(f"任務狀態: {result.status}")
    except Exception as e:
        print(f"任務失敗: {e}")
    
    print("\n所有任務已提交完成！")
    print("請檢查 Celery Worker 的日誌以查看任務執行結果。")

if __name__ == "__main__":
    test_celery_tasks() 