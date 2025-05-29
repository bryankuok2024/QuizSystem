from pathlib import Path
import os

# 加載環境變量
from dotenv import load_dotenv
load_dotenv()

# DEBUG: Print environment variables immediately after load_dotenv()
# print("\n" + "="*20 + " DEBUGGING EMAIL ENV VARS (EARLY) " + "="*20) # 添加調試信息頭
# print(f"DEBUG_EARLY: EMAIL_HOST_USER: '{os.getenv('EMAIL_HOST_USER', 'NOT_SET')}'")
# print(f"DEBUG_EARLY: EMAIL_HOST_PASSWORD: Is set? {'YES' if os.getenv('EMAIL_HOST_PASSWORD') else 'NO_OR_EMPTY'}")
# print(f"DEBUG_EARLY: USE_GMAIL_SMTP: '{os.getenv('USE_GMAIL_SMTP', 'NOT_SET')}'")
# print(f"DEBUG_EARLY: DEFAULT_FROM_EMAIL (from .env if set): '{os.getenv('DEFAULT_FROM_EMAIL', 'NOT_SET')}'")
# print("="*60 + "\n") # 添加調試信息尾

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@=i^4%@^21blfk=voxscjc@58c64b-j4x8a08q1fjq*==y3=ci'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']


# Application definition

INSTALLED_APPS = [
    'quizApp.quizApp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # django-allauth 必需
    
    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'users.apps.UsersConfig',
    'questions.apps.QuestionsConfig',
    'payments.apps.PaymentsConfig',
    'progress.apps.ProgressConfig',
]

# django-allauth 必需的 SITE_ID
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # django-allauth 必需
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quizApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'quizApp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'quiz_db',
        'USER': 'root',
        'PASSWORD': 'Yenoo5581',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'zh-hant'  # 繁體中文
TIME_ZONE = 'Asia/Hong_Kong'  # 香港時區

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 分鐘
CELERY_TASK_SOFT_TIME_LIMIT = 60  # 60 秒

# Celery Beat 配置（用於定時任務）
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# 郵件設置
# print("\n" + "="*20 + " DEBUGGING EMAIL ENV VARS " + "="*20) # 已移動到更早的位置
# print(f"DEBUG: Attempting to read EMAIL_HOST_USER: '{os.getenv('EMAIL_HOST_USER', 'NOT_SET')}'")
# print(f"DEBUG: Attempting to read EMAIL_HOST_PASSWORD: Is set? {'YES' if os.getenv('EMAIL_HOST_PASSWORD') else 'NO_OR_EMPTY'}")
# print(f"DEBUG: Attempting to read USE_GMAIL_SMTP: '{os.getenv('USE_GMAIL_SMTP', 'NOT_SET')}'")
# print("="*50 + "\n")

# 從環境變量中讀取郵件設置（如果沒有則使用預設值）
USE_GMAIL_SMTP = os.getenv('USE_GMAIL_SMTP', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# print("⚠️ DEBUG: Forcing console email backend for testing SMTP issues.") # DEBUG: Reverted
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # DEBUG: Reverted
# DEFAULT_FROM_EMAIL = 'QuizSystem Console <noreply@example.com>' # DEBUG: Reverted
# EMAIL_HOST_USER = 'consoleuser' # DEBUG: Reverted
# EMAIL_HOST_PASSWORD = 'consolepass' # DEBUG: Reverted

if USE_GMAIL_SMTP and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    # 檢測郵件服務商並設置相應的 SMTP 配置
    if '@gmail.com' in EMAIL_HOST_USER or '@yenoo.co' in EMAIL_HOST_USER:
        # Gmail SMTP 配置（包括由 Gmail 託管的自定義域名如 yenoo.co）
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_USE_SSL = False
       
        if '@yenoo.co' in EMAIL_HOST_USER:
            print("✅ 使用 Gmail SMTP 後端（Yenoo 自定義域名，由 Gmail 託管）")
        else:
            print("✅ 使用 Gmail SMTP 後端")
    else:
        # 其他郵件服務的通用配置
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
        EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
        EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
        print("✅ 使用通用 SMTP 後端")
   
    # 通用 SMTP 設置
    # EMAIL_HOST_USER 和 EMAIL_HOST_PASSWORD 已經從 os.getenv 中獲取
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'題庫系統 <{EMAIL_HOST_USER}>')
    SERVER_EMAIL = EMAIL_HOST_USER  # 用於伺服器錯誤通知
   
    # Gmail SMTP 連接設置
    EMAIL_TIMEOUT = 60  # 連接超時（秒）
   
    # Gmail 特定設置（用於提高成功率）
    EMAIL_USE_LOCALTIME = False # Django 默認使用 UTC，通常不需要更改
    # EMAIL_CONNECTION_USE_TLS = True # 這不是一個標準的 Django 設置，應使用 EMAIL_USE_TLS
   
else:
    # 開發環境：使用控制台後端 (如果未使用 SMTP)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'QuizSystem <noreply@quizsystem.com>'
    print("ℹ️ 使用控制台郵件後端（如果 SMTP 未配置或禁用）")

EMAIL_SUBJECT_PREFIX = '[題庫系統] '

# 緩存設置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session 設置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 小時
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # 生產環境設為 True

# 日誌設置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'users': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'questions': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'payments': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'progress': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# 創建日誌目錄
log_dir = BASE_DIR / 'logs'
os.makedirs(log_dir, exist_ok=True)

# ================================
# Django-allauth 配置
# ================================

# 登入/登出 URL 設置
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# allauth 帳戶配置
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # 使用 email 登入
ACCOUNT_EMAIL_REQUIRED = True  # email 必填
ACCOUNT_USERNAME_REQUIRED = False  # 不需要用戶名
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # 強制郵件驗證
ACCOUNT_UNIQUE_EMAIL = True  # 唯一 email

# 註冊設置
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True  # 註冊時需要輸入兩次 email
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True  # 註冊時需要輸入兩次密碼
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5  # 登入嘗試次數限制
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # 登入嘗試超時時間（秒）

# Session 和 Cookie 設置
ACCOUNT_SESSION_REMEMBER = True  # 記住登入狀態
ACCOUNT_LOGOUT_ON_GET = False  # 需要 POST 請求才能登出
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False  # 更改密碼後不自動登出

# Email 設置
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # 郵件確認連結過期天數
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True  # 使用 HMAC 簽名
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 180  # 重新發送確認郵件冷卻時間（秒）

# 密碼設置
ACCOUNT_PASSWORD_MIN_LENGTH = 8  # 密碼最小長度
ACCOUNT_PASSWORD_INPUT_TYPE = 'password'  # 密碼輸入類型

# 用戶名設置（雖然不需要，但保留設置）
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'root', 'administrator', 'test', 'quiz', 'system']

# 表單設置
ACCOUNT_FORMS = {
    # 可以自定義表單
    # 'signup': 'users.forms.CustomSignupForm',
    # 'login': 'users.forms.CustomLoginForm',
}

# 適配器設置（可用於自定義行為）
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'

# 社交帳戶設置（如果需要的話）
SOCIALACCOUNT_PROVIDERS = {
    # 'google': {
    #     'SCOPE': [
    #         'profile',
    #         'email',
    #     ],
    #     'AUTH_PARAMS': {
    #         'access_type': 'online',
    #     }
    # }
}

# 自定義 allauth 模板標籤（可選）
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'  # 生產環境改為 'https'

# 用戶模型設置（如果有自定義用戶模型）
# AUTH_USER_MODEL = 'users.CustomUser'

# 繁體中文本地化設置
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[題庫系統] '

# 開發環境特殊設置
if DEBUG:
    # 開發環境下可以跳過郵件驗證（僅用於測試）
    # ACCOUNT_EMAIL_VERIFICATION = 'optional'
    pass

print("\nDEBUGGING URLS.PY LOADING:")
try:
    from quizApp import urls as quiz_app_urls
    print(f"Successfully imported quizApp.urls. Path: {quiz_app_urls.__file__}")
    if hasattr(quiz_app_urls, 'urlpatterns'):
        print(f"quizApp.urls has urlpatterns. Number of patterns: {len(quiz_app_urls.urlpatterns)}")
        print("Patterns found:")
        for i, pattern in enumerate(quiz_app_urls.urlpatterns):
            print(f"  {i}: {pattern}")
    else:
        print("quizApp.urls does NOT have urlpatterns attribute!")
except ImportError as e:
    print(f"Failed to import quizApp.urls. ImportError: {e}")
except Exception as e:
    print(f"An unexpected error occurred while trying to import quizApp.urls: {e}")
print("END DEBUGGING URLS.PY LOADING\n")
