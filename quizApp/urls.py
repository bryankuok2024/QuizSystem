from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from quizApp.quizApp import views as app_views # Import your app's views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom multi-step signup URLs - these might be part of a different flow now
    # path('accounts/signup/profile/', app_views.signup_profile_view, name='account_signup_profile'),
    # path('accounts/signup/verify-email/', app_views.signup_verify_email_view, name='account_signup_verify_email'),
    # path('accounts/signup/set-password/', app_views.signup_set_password_view, name='account_signup_set_password'),

    path('accounts/register/', app_views.signup_options_view, name='signup_options'), # New page for choosing signup method
    path('accounts/', include('allauth.urls')), # Keep allauth for login, password reset etc. and its own 'account_signup'
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('debug/', TemplateView.as_view(template_name='debug.html'), name='debug'),
    path('test/', TemplateView.as_view(template_name='test.html'), name='test'),
    path('test-email/', app_views.test_send_email_view, name='test_send_email'), # Added path for existing test_send_email_view
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 