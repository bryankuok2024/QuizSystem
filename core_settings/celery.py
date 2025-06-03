import os
from celery import Celery

# 設置 Django settings 模塊
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_settings.settings')

# 創建 Celery 實例
app = Celery('quizApp') # Name can be project-specific, keeping as is for now

# 使用 Django 設置配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動發現任務
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 