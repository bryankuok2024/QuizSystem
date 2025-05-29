"""
URL configuration for quizApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views as app_views # MODIFIED: Changed to relative import

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Custom signup options page
    path('accounts/register/', app_views.signup_options_view, name='signup_options'),
    path('accounts/users/', include('users.urls')),

    # Django-allauth URLs
    path('accounts/', include('allauth.urls')),
    
    # 主頁
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # 調試和測試頁面
    path('debug/', TemplateView.as_view(template_name='debug.html'), name='debug'),
    path('test/', TemplateView.as_view(template_name='test.html'), name='test'),
    path('send-test-email/', app_views.test_send_email_view, name='send_test_email'),
    
    # 應用 URLs（暫時註釋掉）
    # path('users/', include('users.urls')),
    # path('questions/', include('questions.urls')),
    # path('payments/', include('payments.urls')),
    # path('progress/', include('progress.urls')),
]

print(f"DEBUG: In quizApp/urls.py - urlpatterns initially has {len(urlpatterns)} items:")
for i, p_item in enumerate(urlpatterns):
    try:
        # Try to get a meaningful representation, like the route or name
        route_str = str(p_item.pattern)
    except AttributeError:
        route_str = str(p_item) # Fallback for include() or other types
    print(f"  {i}: Pattern: {route_str}")

# 開發環境下的靜態文件和媒體文件服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    print(f"DEBUG: In quizApp/urls.py - after adding static/media, urlpatterns has {len(urlpatterns)} items.")
    # Optional: print the last few items to see static/media
    if len(urlpatterns) > len(urlpatterns) -2: #  Ensure we have at least the static and media URLs to print
        for i in range(len(urlpatterns) -2, len(urlpatterns)):
            p_item = urlpatterns[i]
            try:
                route_str = str(p_item.pattern)
            except AttributeError:
                route_str = str(p_item)
            print(f"  {i}: Pattern: {route_str} (added in DEBUG)")
