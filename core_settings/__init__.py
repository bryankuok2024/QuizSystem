# 這將確保 app 在 Django 啟動時被加載
from .celery import app as celery_app

__all__ = ('celery_app',) 