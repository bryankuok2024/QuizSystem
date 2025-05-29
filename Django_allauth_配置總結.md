# Django-allauth 配置總結

## 項目概述
- **項目名稱**: quizApp (題庫系統)
- **Django 版本**: 5.2.1
- **django-allauth 版本**: 65.8.1
- **數據庫**: MySQL (quiz_db)
- **語言**: 繁體中文 (zh-hant)
- **時區**: Asia/Hong_Kong

## 已完成的配置

### 1. 安裝和基本設置
✅ 安裝 django-allauth  
✅ 配置 INSTALLED_APPS  
✅ 配置 AUTHENTICATION_BACKENDS  
✅ 配置 MIDDLEWARE  
✅ 設置 SITE_ID = 1  

### 2. URL 配置
✅ 主 URLs 配置 (`quizApp/urls.py`)  
✅ 包含 allauth URLs: `path('accounts/', include('allauth.urls'))`  
✅ 主頁模板配置  

### 3. 模板系統
✅ 創建 `templates/` 目錄  
✅ 基礎模板 `base.html` (包含導航欄和 allauth 連結)  
✅ 主頁模板 `home.html` (響應式設計，Bootstrap 5)  

### 4. Django-allauth 設置
✅ **Email 註冊**: 使用 email 作為主要登入方式  
✅ **強制郵件驗證**: `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'`  
✅ **唯一 Email**: `ACCOUNT_UNIQUE_EMAIL = True`  
✅ **登入/登出 URL**: 配置重定向路徑  
✅ **密碼要求**: 最小長度 8 字符  
✅ **速率限制**: 登入失敗和郵件確認限制  

### 5. 數據庫遷移
✅ 執行 `python manage.py migrate`  
✅ 創建 allauth 相關數據表  
✅ 創建超級用戶帳戶  

### 6. 測試驗證
✅ Django 系統檢查通過  
✅ 數據庫連接測試通過  
✅ allauth 配置驗證通過  
✅ 用戶模型測試通過  

## 主要功能

### 用戶認證功能
- ✅ Email 註冊
- ✅ Email 登入
- ✅ 郵件驗證
- ✅ 密碼重置
- ✅ 登出功能
- ✅ 記住登入狀態

### 安全特性
- ✅ CSRF 保護
- ✅ 登入嘗試限制
- ✅ 郵件確認冷卻時間
- ✅ 密碼強度要求
- ✅ 用戶名黑名單

## 文件結構
```
quizApp/
├── manage.py
├── quizApp/
│   ├── __init__.py
│   ├── settings.py          # 主要配置文件
│   ├── urls.py              # URL 路由配置
│   ├── wsgi.py
│   └── asgi.py
├── templates/
│   ├── base.html            # 基礎模板
│   └── home.html            # 主頁模板
├── users/                   # 用戶應用
├── questions/               # 題目應用
├── payments/                # 支付應用
├── progress/                # 進度應用
└── test_allauth.py          # 配置測試腳本
```

## 重要的 URL 路徑

| 功能 | URL | 說明 |
|------|-----|------|
| 主頁 | `/` | 系統首頁 |
| 註冊 | `/accounts/signup/` | 用戶註冊 |
| 登入 | `/accounts/login/` | 用戶登入 |
| 登出 | `/accounts/logout/` | 用戶登出 |
| 密碼重置 | `/accounts/password/reset/` | 重置密碼 |
| 郵件確認 | `/accounts/confirm-email/` | 確認郵件地址 |
| 管理後台 | `/admin/` | Django 管理界面 |

## 配置文件重點

### settings.py 關鍵設置
```python
# 應用配置
INSTALLED_APPS = [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... 其他應用
]

# 認證後端
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# allauth 配置
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

## 使用說明

### 啟動開發服務器
```bash
# 激活虛擬環境
venv\Scripts\Activate.ps1

# 進入項目目錄
cd quizApp

# 啟動服務器
python manage.py runserver
```

### 訪問系統
1. **主頁**: http://127.0.0.1:8000/
2. **註冊**: http://127.0.0.1:8000/accounts/signup/
3. **登入**: http://127.0.0.1:8000/accounts/login/
4. **管理後台**: http://127.0.0.1:8000/admin/

### 測試配置
```bash
python test_allauth.py
```

## 注意事項

### 開發環境
- 郵件後端設置為控制台輸出 (`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`)
- 郵件驗證連結會在控制台中顯示
- DEBUG = True

### 生產環境準備
- [ ] 更改 `SECRET_KEY`
- [ ] 設置 `DEBUG = False`
- [ ] 配置真實的 SMTP 郵件服務
- [ ] 設置 `ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'`
- [ ] 配置靜態文件服務
- [ ] 設置適當的 `ALLOWED_HOSTS`

## 下一步開發

### 待實現功能
- [ ] 自定義用戶註冊表單
- [ ] 用戶個人資料頁面
- [ ] 社交登入 (Google, Facebook 等)
- [ ] 題庫功能實現
- [ ] 支付系統集成
- [ ] 學習進度追蹤

### 應用 URLs 配置
目前應用的 URLs 已創建但暫時註釋掉，需要時可以取消註釋：
```python
# 在 quizApp/urls.py 中
path('users/', include('users.urls')),
path('questions/', include('questions.urls')),
path('payments/', include('payments.urls')),
path('progress/', include('progress.urls')),
```

## 總結
Django-allauth 已成功配置並可以正常使用。系統支持 Email 註冊和登入，包含完整的郵件驗證流程。所有基礎功能都已測試通過，可以開始進行具體的業務功能開發。 