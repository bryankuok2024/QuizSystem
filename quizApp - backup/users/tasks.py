from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(user_email, username):
    """
    發送歡迎郵件給新註冊用戶
    """
    try:
        subject = '歡迎加入題庫系統！'
        message = f'你好 {username}，歡迎加入我們的題庫學習系統！'
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f"歡迎郵件已發送給 {user_email}")
        return f"歡迎郵件已發送給 {user_email}"
    except Exception as e:
        logger.error(f"發送歡迎郵件失敗: {str(e)}")
        raise

@shared_task
def send_password_reset_email(user_email, reset_link):
    """
    發送密碼重置郵件
    """
    try:
        subject = '密碼重置請求'
        message = f'請點擊以下連結重置您的密碼：{reset_link}'
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f"密碼重置郵件已發送給 {user_email}")
        return f"密碼重置郵件已發送給 {user_email}"
    except Exception as e:
        logger.error(f"發送密碼重置郵件失敗: {str(e)}")
        raise 