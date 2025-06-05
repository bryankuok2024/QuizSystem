# Django-allauth 配置總結

## 項目概述
- **項目名稱**: QUIZSYSTEM (題庫系統)
- **Django 版本**: 5.2.1
- **django-allauth 版本**: 0.62.0
- **數據庫**: MySQL (默認為 quiz_db，可通過 .env 配置)
- **語言**: 繁體中文 (zh-hant)
- **時區**: Asia/Hong_Kong

## 已完成的配置

### 1. 安裝和基本設置
✅ 安裝 django-allauth
✅ 配置 INSTALLED_APPS (在 `core_settings/settings.py`)
✅ 配置 AUTHENTICATION_BACKENDS (在 `core_settings/settings.py`)
✅ 配置 MIDDLEWARE (在 `core_settings/settings.py`)
✅ 設置 SITE_ID = 1 (在 `core_settings/settings.py`)

### 2. URL 配置
✅ 主 URLs 配置 (`core_settings/urls.py`)
✅ 包含 allauth URLs: `path('accounts/', include('allauth.urls'))`
✅ 主頁模板配置

### 3. 模板系統
✅ 創建 `templates/` 目錄 (在項目根目錄)
✅ 基礎模板 `base.html` (包含導航欄和 allauth 連結)
✅ 主頁模板 `home.html` (響應式設計，Bootstrap 5)

### 4. Django-allauth 設置 (部分配置通過 `.env` 文件加載)
✅ **Email 註冊**: 使用 email 作為主要登入方式 (`ACCOUNT_AUTHENTICATION_METHOD = 'email'`, `ACCOUNT_LOGIN_METHODS = ['email']`)
✅ **用戶名非必需**: `ACCOUNT_USERNAME_REQUIRED = False`, `ACCOUNT_USER_MODEL_USERNAME_FIELD = None`
✅ **郵件驗證**: `ACCOUNT_EMAIL_VERIFICATION` (通過 `.env` 設置，默認為 `'none'`)
✅ **唯一 Email**: `ACCOUNT_UNIQUE_EMAIL = True`
✅ **登入/登出 URL**: 配置重定向路徑 (`LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`)
✅ **密碼要求**: 最小長度 8 字符 (`ACCOUNT_PASSWORD_MIN_LENGTH = 8`)
✅ **速率限制**: 登入失敗和郵件確認限制 (`ACCOUNT_RATE_LIMITS`)
✅ **Google 社交登入**: 已配置 `SOCIALACCOUNT_PROVIDERS` for Google (Client ID 和 Secret 通過 `.env` 加載)
✅ **自定義表單和適配器**: `ACCOUNT_FORMS`, `ACCOUNT_ADAPTER`, `SOCIALACCOUNT_ADAPTER` 已指向 `users` 應用中的自定義實現。

### 5. 數據庫遷移
✅ 執行 `python manage.py migrate`
✅ 創建 allauth 相關數據表
✅ 創建超級用戶帳戶

### 6. 測試驗證
✅ Django 系統檢查通過 (`python manage.py check`)
✅ 數據庫連接測試通過 (通過 `runserver` 和訪問頁面確認)
✅ allauth 配置驗證通過 (註冊、登入、登出、社交登錄功能基本正常)
✅ 用戶模型測試通過 (與 allauth 交互正常)

## 主要功能

### 用戶認證功能
- ✅ Email 註冊
- ✅ Email 登入
- ✅ 郵件驗證 (根據 `.env` 配置)
- ✅ 密碼重置
- ✅ 登出功能
- ✅ 記住登入狀態
- ✅ Google 社交帳號登入

### 安全特性
- ✅ CSRF 保護
- ✅ 登入嘗試限制
- ✅ 密碼強度要求

## 文件結構 (主要部分)
```
QUIZSYSTEM/
├── .env                   # 環境變量 (gitignore, 不提交到版本庫)
├── environment_template.txt # .env 的模板
├── manage.py              # Django 管理腳本
├── requirements.txt       # Python 依賴
├── core_settings/         # Django 項目核心配置
│   ├── __init__.py
│   ├── settings.py          # 主要配置文件
│   ├── urls.py              # 主 URL 路由配置
│   ├── wsgi.py
│   └── asgi.py
├── templates/             # 全局 HTML 模板
│   ├── base.html
│   ├── home.html
│   └── account/           # allauth 模板覆蓋 (如果需要)
├── static/                # 全局靜態文件 (CSS, JS, Images)
├── users/                 # 用戶應用 (包含 models, views, forms, adapters)
├── questions/             # 題目應用
├── payments/              # 支付應用
├── progress/              # 進度應用
├── logs/                  # 日誌文件目錄
└── ... (其他應用和文件)
```

## 重要的 URL 路徑

| 功能 | URL | 說明 |
|------|-----|------|
| 主頁 | `/` | 系統首頁 |
| 註冊 | `/accounts/signup/` | 用戶註冊 |
| 登入 | `/accounts/login/` | 用戶登入 |
| 登出 | `/accounts/logout/` | 用戶登出 |
| 密碼重置 | `/accounts/password/reset/` | 重置密碼 |
| 郵件確認 | `/accounts/confirm-email/` | 確認郵件地址 (如果啟用) |
| Google登入 | `/accounts/google/login/` | Google 社交登入流程起始點 |
| 管理後台 | `/admin/` | Django 管理界面 |

## 配置文件重點

### `core_settings/settings.py` 關鍵設置示例
```python
# INSTALLED_APPS (部分)
INSTALLED_APPS = [
    # ... django apps ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # Google Provider
    # ... your local apps ...
    'users.apps.UsersConfig',
    # ...
]

SITE_ID = 1

# AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Django-allauth Core
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGIN_METHODS = ['email'] # New setting for login methods

# Email verification (loaded from .env, example default shown here)
ACCOUNT_EMAIL_VERIFICATION = os.getenv('ACCOUNT_EMAIL_VERIFICATION', 'none')
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = os.getenv('ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION', 'False').lower() == 'true'


# URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Adapters and Forms
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'
ACCOUNT_FORMS = {'signup': 'users.forms.CustomSignupForm'}

# Social Account Settings
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none' # Or as per your policy
SOCIALACCOUNT_EMAIL_REQUIRED = True

# Google Provider Specific (client_id & secret loaded from .env)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# Other settings like rate limits, password length etc.
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',
    'confirm_email': '1/3m',
}
```

## 使用說明

### 環境設置
1.  確保已安裝 Python 和 pip。
2.  克隆項目到本地。
3.  創建並激活虛擬環境 (例如 `python -m venv venv` 和 `venv\\Scripts\\activate.ps1` 或 `source venv/bin/activate`)。
4.  安裝依賴: `pip install -r requirements.txt`
5.  複製 `environment_template.txt` 為 `.env`。
6.  編輯 `.env` 文件，填寫所有必要的配置 (如 `SECRET_KEY`, 數據庫憑證, Google OAuth 憑證等)。

### 啟動開發服務器
```bash
# 激活虛擬環境 (如果尚未激活)
# venv\\Scripts\\Activate.ps1  (Windows)
# source venv/bin/activate (Linux/macOS)

# 項目根目錄 (QUIZSYSTEM/)
python manage.py check
python manage.py migrate
python manage.py runserver
```

### 訪問系統
1. **主頁**: http://127.0.0.1:8000/
2. **註冊**: http://127.0.0.1:8000/accounts/signup/
3. **登入**: http://127.0.0.1:8000/accounts/login/
4. **管理後台**: http://127.0.0.1:8000/admin/ (需要先創建超級用戶 `python manage.py createsuperuser`)

### 測試配置腳本
(移除了對 `test_allauth.py` 的引用，除非您確認該文件仍然相關且已更新)

## 注意事項

### 開發環境
- `.env` 文件中的 `DEBUG` 通常設置為 `True`。
- 郵件後端可能設置為控制台輸出 (如果 `USE_GMAIL_SMTP=False` in `.env`)。
- `ACCOUNT_DEFAULT_HTTP_PROTOCOL` 在 `.env` 中通常設為 `http`。

### 生產環境準備
- [ ] 生成一個強壯的 `SECRET_KEY` 並在 `.env` 中設置。
- [ ] 在 `.env` 中設置 `DEBUG = False`。
- [ ] 在 `.env` 中配置真實的 SMTP 郵件服務 (`USE_GMAIL_SMTP=True` 和相關憑證)。
- [ ] 在 `.env` 中設置 `ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'`。
- [ ] 配置靜態文件服務 (例如 `python manage.py collectstatic` 並使用 Nginx/Apache 服務 `staticfiles/` 目錄)。
- [ ] 在 `.env` 中設置正確的 `ALLOWED_HOSTS`。
- [ ] 在 `.env` 中設置 `SESSION_COOKIE_SECURE = True`。
- [ ] 檢查所有日誌配置。
- [ ] 確保 Redis 服務在生產環境中穩定運行並配置了密碼 (如果需要)。

## 下一步開發

### 待實現/完善功能
- [ ] 用戶個人資料頁面
- [ ] 題庫功能詳細實現
- [ ] 支付系統集成細節
- [ ] 學習進度追蹤細節
- [ ] 更細致的權限管理
- [ ] 單元測試和集成測試覆蓋

### 應用 URLs 配置
應用特定的 URLs 應在其各自應用的 `urls.py` 文件中定義，並在 `core_settings/urls.py` 中包含。例如：
```python
# 在 core_settings/urls.py 中
from django.urls import path, include

urlpatterns = [
    # ...
    path('users/', include('users.urls')),
    path('questions/', include('questions.urls')),
    path('payments/', include('payments.urls')),
    path('progress/', include('progress.urls')),
    # ...
]
```

## 總結
Django-allauth 已成功配置並與重構後的項目結構集成。系統支持 Email 註冊、登入，以及 Google 社交登入。郵件驗證、密碼重置等核心認證流程已具備。開發者應確保 `.env` 文件配置正確，並遵循生產環境準備清單以進行部署。 

# TEMPLATES - 上下文處理器重要說明 (針對 allauth 0.61.0+)
# 不應在 TEMPLATES 的 context_processors 中手動添加 'allauth.account.context_processors.account' 
# 或 'allauth.socialaccount.context_processors.socialaccount'，這些已不再需要，且會導致 ModuleNotFoundError。
# Django 的 'django.template.context_processors.request' 是 allauth 所需的。

# Google OAuth 登入詳細配置要點 (更多細節請參考 README.md):
# 1. settings.py: SITE_ID = 1
# 2. Google Cloud Console: 配置 OAuth Client ID 和 Secret, 並設置正確的重定向 URI (例如 http://127.0.0.1:8000/accounts/google/login/callback/)
# 3. Django Admin (/admin/socialaccount/socialapp/): 創建 Social Application, 選擇 "Google" Provider, 填入 Client ID 和 Secret, 並關聯到正確的 Site.

# Other settings like rate limits, password length etc.
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',
    'confirm_email': '1/3m',
} 