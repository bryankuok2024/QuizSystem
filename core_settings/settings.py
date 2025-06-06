# core_settings/settings.py (替换为以下全部内容)

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path, verbose=True, override=True)

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_fallback_secret_key_if_not_set_in_env')
DEBUG = os.getenv('DEBUG', 'True').lower() != 'false'
ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    # Local apps first
    'users.apps.UsersConfig',
    'questions.apps.QuestionsConfig',
    'payments.apps.PaymentsConfig',
    'progress.apps.ProgressConfig',

    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth
    
    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # Example: Google provider
    'widget_tweaks', # Added django-widget-tweaks
]

# Set our custom user model
AUTH_USER_MODEL = 'users.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Required by allauth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # Required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Allauth specific context processors (REMOVED based on new findings):
                # 'allauth.account.context_processors.account',
                # 'allauth.socialaccount.context_processors.socialaccount',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Needed for Django admin
    'allauth.account.auth_backends.AuthenticationBackend', # allauth specific authentication methods
]

WSGI_APPLICATION = 'core_settings.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME', 'quiz_db'),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Hong_Kong'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================================
# Django-allauth Consolidated Settings
# =======================================
SITE_ID = 1

# General Redirects (used by allauth)
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Core Account Settings
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional' # Values: 'optional', 'mandatory', 'none'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_FIELDS = ['email'] # Customize as needed, e.g., ['username', 'email']
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.getenv('ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'http')
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[題庫系統] '
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_FORMS = {
    'login': 'allauth.account.forms.LoginForm',
    'signup': 'allauth.account.forms.SignupForm',
    # Add other forms here if you customize them
}

# Social Account Settings
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = os.getenv('SOCIALACCOUNT_AUTO_SIGNUP', 'True').lower() == 'true'
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional' # Mirrors account email verification
SOCIALACCOUNT_LOGIN_ON_GET = True

# Load OAuth credentials from .env (used if SOCIALACCOUNT_PROVIDERS.APP is configured)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
# APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID') # Example
# ... other Apple env vars if needed ...

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # 'APP': { # Relying on SocialApp in DB for now.
        #     'client_id': GOOGLE_CLIENT_ID,
        #     'secret': GOOGLE_CLIENT_SECRET,
        #     'key': ''
        # },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    },
    # 'apple': { # Example for Apple
    #     # ... Apple specific provider config ...
    # }
}
# =======================================
# End of Django-allauth Settings
# =======================================

# Celery Configuration (Ensure these are correct for your setup)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
if REDIS_PASSWORD:
    CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@localhost:6379/0'
    CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@localhost:6379/0'
else:
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Email Settings (Ensure these are correct for your setup)
FINAL_USE_GMAIL_SMTP = os.getenv('USE_GMAIL_SMTP', 'False').lower() == 'true'
FINAL_EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
FINAL_EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
FINAL_DEFAULT_FROM_EMAIL_ENV = os.getenv('DEFAULT_FROM_EMAIL', '')

if FINAL_USE_GMAIL_SMTP and FINAL_EMAIL_HOST_USER and FINAL_EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    if '@gmail.com' in FINAL_EMAIL_HOST_USER or '@yenoo.co' in FINAL_EMAIL_HOST_USER: # Specific logic for your domains
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_USE_SSL = False
    else: # Generic SMTP from .env
        EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
        EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
        EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
    EMAIL_HOST_USER = FINAL_EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = FINAL_EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = FINAL_DEFAULT_FROM_EMAIL_ENV if FINAL_DEFAULT_FROM_EMAIL_ENV else f'QuizSystem <{FINAL_EMAIL_HOST_USER}>'
    SERVER_EMAIL = FINAL_EMAIL_HOST_USER # Or your preferred server email
    EMAIL_TIMEOUT = 60
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'QuizSystem Console <noreply@example.com>'
    # Clear SMTP vars if console backend is used
    EMAIL_HOST_USER = None
    EMAIL_HOST_PASSWORD = None
    EMAIL_HOST = None
    EMAIL_PORT = None
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = False

# Caches (Ensure these are correct)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CELERY_RESULT_BACKEND, # Assuming same Redis instance
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}
    }
}

# Allow social account signup to log the user in immediately
SOCIALACCOUNT_LOGIN_ON_SIGNUP = True

# Session Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

# Logging (Ensure paths and levels are correct)
LOGGING_DIR = BASE_DIR / 'logs'
LOGGING_DIR.mkdir(exist_ok=True) # Create logs directory if it doesn't exist

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}', 'style': '{'},
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGGING_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {'handlers': ['file', 'console'], 'level': 'INFO', 'propagate': True},
        'users': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': True},
        # Add other app loggers as needed
    },
}
