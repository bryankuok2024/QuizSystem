from celery import shared_task
from django.core.mail import send_mail as django_send_mail
from django.conf import settings

@shared_task(bind=True, max_retries=3, default_retry_delay=60) # bind=True to access self, retry 3 times with 60s delay
def send_email_task(self, subject, message, recipient_list, html_message=None, from_email=None):
    """
    異步發送郵件的 Celery 任務。
    """
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        django_send_mail(
            subject=subject,
            message=message, # text content
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message, # html content (optional)
            fail_silently=False,
        )
        # print(f"[Celery Task] Email sent to {recipient_list} with subject: {subject}") # For debugging
        return f"Email successfully sent to {', '.join(recipient_list)}"
    except Exception as e:
        # print(f"[Celery Task] Error sending email to {recipient_list}: {e}") # For debugging
        # Retry the task if an exception occurs (e.g., SMTP server down)
        # self.retry(exc=e) # This will use the default_retry_delay
        # Or, to be more specific with retry countdown:
        raise self.retry(exc=e, countdown=int(self.default_retry_delay * (self.request.retries + 1))) 