# QuizSystem 題庫系統

一個基於 Django 的高安全性、功能豐富的線上題庫學習平台。

## 功能特點

### 🎯 核心功能
- **用戶認證** - Email/Google 註冊、登入、郵件驗證、密碼重置。
- **科目與題目** - 多級科目分類、題目管理、支持多種題型、試玩題目設置。
- **互動練習** - 科目順序練習、單題練習、錯題本練習、練習中顯示答案。
- **進度追蹤** - 自動記錄用戶答題進度與正確率。
- **題目搜索** - 按關鍵詞、科目、標籤等多維度篩選題目。
- **書籤收藏** - 方便用戶收藏和管理重要題目。
- **安全加固** - 全站路由採用ID混淆技術，防止惡意枚舉和未授權訪問 (IDOR)。
- **管理後台** - 功能完善的後台管理界面，方便管理用戶、科目和題目。

### 🔧 技術特性
- **Django 5.2.1** - 現代 Python Web 框架
- **django-allauth 0.62.0** - 強大的用戶認證管理
- **django-filter** - 優雅的查詢過濾
- **hashids** - URL安全混淆
- **MySQL** - 可靠的關聯式數據庫 (通過 `.env` 配置)
- **Redis** - 用於 Celery 消息代理、結果後端和 Django 緩存/會話 (通過 `.env` 配置密碼)
- **Celery** - 異步任務處理 (通過 `.env` 配置 Broker/Backend URL)
- **Bootstrap 5** - 響應式前端設計
- **環境變量驅動配置** - 使用 `.env` 文件管理敏感信息和環境特定配置

## 項目結構 (主要部分)

```
QUIZSYSTEM/
├── .env                   # 環境變量 (gitignore, 不提交到版本庫)
├── environment_template.txt # .env 的模板
├── manage.py              # Django 管理腳本
├── requirements.txt       # Python 依賴
├── core_settings/         # Django 項目核心配置
│   ├── __init__.py
│   ├── settings.py          # 主要配置文件 (從 .env 加載配置)
│   ├── urls.py              # 主 URL 路由配置
│   ├── wsgi.py
│   └── asgi.py
├── templates/             # 全局 HTML 模板 (包括 allauth 和各 app 的模板)
│   ├── base.html
│   ├── home.html
│   ├── account/
│   └── questions/
├── static/                # 全局靜態文件 (CSS, JS, Images)
├── users/                 # 用戶應用 (models, views, forms, custom allauth adapters)
├── questions/             # 題目應用
├── payments/              # 支付應用
├── progress/              # 進度應用
├── docs/                  # 項目文檔 (包括本文件)
├── venv/                  # Python 虛擬環境 (建議)
└── .gitignore             # Git 忽略文件配置
```

## 安裝與設置

### 環境要求
- Python 3.8+
- MySQL 5.7+ (或兼容版本)
- Redis 5.0+ (或兼容版本)
- Git

### 安裝步驟

1.  **克隆項目**
    ```bash
    git clone https://github.com/bryankuok2024/QuizSystem.git # 或者你的倉庫 URL
    cd QuizSystem
    ```

2.  **創建並激活虛擬環境**
    ```bash
    # Windows
    python -m venv venv
    .\\venv\\Scripts\\activate.ps1

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安裝依賴**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置環境變量**
    *   複製 `environment_template.txt` 並重命名為 `.env`:
        ```bash
        # Windows
        copy environment_template.txt .env

        # Linux/macOS
        cp environment_template.txt .env
        ```
    *   編輯 `.env` 文件，填寫所有必要的配置項。**至少需要配置以下內容才能啟動：**
        *   `SECRET_KEY` (生成一個新的隨機密鑰，例如使用 `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
        *   `DATABASE_NAME`
        *   `DATABASE_USER`
        *   `DATABASE_PASSWORD`
        *   `DATABASE_HOST`
        *   `DATABASE_PORT`
        *   `GOOGLE_CLIENT_ID` (如果需要 Google 登入)
        *   `GOOGLE_CLIENT_SECRET` (如果需要 Google 登入)
        *   `SITE_ID=1` (Django Sites 框架配置，`django-allauth` 需要，通常在 `settings.py` 中設置)
        *   根據需要配置郵件服務 (`USE_GMAIL_SMTP`, `EMAIL_HOST_USER`, 等) 和 Redis 密碼 (`REDIS_PASSWORD`)。

    *   **關於 `django-allauth` (版本 0.62.0+) 的重要說明**:
        *   您 **不應** 在 `settings.py` 的 `TEMPLATES` 配置中手動添加 `allauth.account.context_processors.account` 或 `allauth.socialaccount.context_processors.socialaccount`。這些在舊版本中可能需要，但在 `0.61.0` 及更高版本中已不再需要，添加它们會導致 `ModuleNotFoundError`。
        *   確保 `allauth` (`'allauth'`)，`allauth.account` (`'allauth.account'`) 和 `allauth.socialaccount` (`'allauth.socialaccount'`) 包含在 `settings.py` 的 `INSTALLED_APPS` 中。

    *   **Google OAuth 登入詳細配置**:
        1.  **`settings.py`**: 確保 `SITE_ID = 1`。
        2.  **Google Cloud Console**:
            *   創建或選擇一個 OAuth 2.0 客戶端 ID。
            *   在 "已授權的重新導向 URI" (Authorized redirect URIs) 中，添加 `http://127.0.0.1:8000/accounts/google/login/callback/` (開發環境) 或對應的生產環境 URL。
        3.  **Django Admin**:
            *   訪問 `/admin/socialaccount/socialapp/`。
            *   點擊 "新增 social application"。
            *   提供者 (Provider): 選擇 "Google"。
            *   名稱 (Name): 例如 "Google API"。
            *   客戶端 ID (Client ID): 填入您從 Google Cloud Console 獲取的 `GOOGLE_CLIENT_ID`。
            *   密鑰 (Secret key): 填入您從 Google Cloud Console 獲取的 `GOOGLE_CLIENT_SECRET`。
            *   站點 (Sites): 從左側選擇框中選擇與 `SITE_ID = 1` 對應的站點 (例如 `127.0.0.1:8000`)，然後點擊箭頭將其移動到右側的 "Chosen sites" 框中。
            *   保存。

5.  **數據庫設置**
    *   確保你的 MySQL 服務正在運行。
    *   在 MySQL 中創建一個數據庫 (例如，名稱與 `.env` 中的 `DATABASE_NAME` 一致)：
        ```sql
        CREATE DATABASE quiz_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        -- 確保 .env 中的 DATABASE_USER 對此數據庫有權限。
        ```

6.  **執行數據庫遷移**
    ```bash
    python manage.py migrate
    ```

7.  **創建超級用戶 (可選, 用於訪問 Django Admin)**
    ```bash
    python manage.py createsuperuser
    ```

8.  **收集靜態文件 (生產環境需要，開發環境 Django 會自動處理)**
    ```bash
    # python manage.py collectstatic # 通常在部署前運行
    ```

## 運行項目 (開發模式)

### 1. 啟動 Redis 服務器
確保 Redis 服務器正在運行。如果 Redis 配置了密碼，請確保 `.env` 文件中的 `REDIS_PASSWORD` 已正確設置。
```bash
# 示例 (取決於你的 Redis 安裝方式)
# Windows (如果使用 WSL 或 Docker):
# sudo systemctl start redis-server (在 WSL 內)
# docker run -d -p 6379:6379 redis

# Linux:
# sudo systemctl start redis-server

# macOS (使用 Homebrew):
# brew services start redis
```
如果你在本機直接運行 `redis-server.exe` (如 `Redis-portable` 中的)，確保它在監聽正確的端口且沒有密碼，或者 `.env` 中未設置 `REDIS_PASSWORD`。

### 2. 啟動 Celery Worker (異步任務處理)
在項目根目錄 (`QUIZSYSTEM/`) 下打開一個新的終端：
```bash
# 激活虛擬環境 (如果尚未激活)
# .\\venv\\Scripts\\activate.ps1 (Windows)
# source venv/bin/activate (Linux/macOS)

celery -A core_settings worker -l info -P eventlet # Windows 使用 eventlet
# celery -A core_settings worker -l info (Linux/macOS)
```
**注意**: `core_settings` 是包含 `celery.py` 的 Django 項目配置目錄名。如果遇到 `billiard` 相關的 `OSError: [WinError 87] The parameter is incorrect` 錯誤，請確保你使用的是 `-P eventlet` (Windows) 或者嘗試 `-P gevent` 或 `-P solo` (後者用於調試，非生產)。

### 3. 啟動 Django 開發服務器
在項目根目錄 (`QUIZSYSTEM/`) 下打開另一個新的終端：
```bash
# 激活虛擬環境 (如果尚未激活)
python manage.py check # 檢查項目配置
python manage.py runserver
```
服務器通常運行在 `http://127.0.0.1:8000/`。

### 4. 啟動 Celery Beat (可選, 用於定時任務)
如果項目中定義了定時任務，在項目根目錄下打開另一個新的終端：
```bash
# 激活虛擬環境
celery -A core_settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 主要訪問路徑
- **主頁**: `http://127.0.0.1:8000/`
- **註冊**: `http://127.0.0.1:8000/accounts/signup/`
- **登入**: `http://127.0.0.1:8000/accounts/login/`
- **Google 登入**: `http://127.0.0.1:8000/accounts/google/login/`
- **題目搜索**: `http://127.0.0.1:8000/questions/search/`
- **我的收藏**: `http://127.0.0.1:8000/questions/bookmarks/`
- **管理後台**: `http://127.0.0.1:8000/admin/`

## 部署 (簡要提示)

生產環境部署是一個複雜的過程，以下僅為概要提示：
1.  **安全**:
    *   `.env` 文件: `DEBUG=False`, 強 `SECRET_KEY`, `ALLOWED_HOSTS` 設為你的域名, `SESSION_COOKIE_SECURE=True`, `ACCOUNT_DEFAULT_HTTP_PROTOCOL='https'`。
    *   配置 HTTPS。
2.  **Web 服務器**: 使用 Gunicorn 或 uWSGI 作為應用服務器。
3.  **反向代理**: 使用 Nginx 或 Apache 處理靜態文件、緩存、負載均衡和 SSL 終止。
4.  **靜態文件**: 運行 `python manage.py collectstatic` 並由 Nginx/Apache 提供服務。
5.  **數據庫**: 使用生產級別的數據庫服務，並定期備份。
6.  **Redis/Celery**: 確保 Redis 和 Celery workers/beat 在生產環境中穩定運行 (例如使用 Supervisor 或 systemd 管理進程)。
7.  **日誌**: 配置完善的日誌記錄和監控。

## 貢獻

歡迎提交 Pull Request 或報告 Issue！

## 授權

本項目採用 MIT 授權條款。

## 聯繫方式

- 作者：Bryan Kuok
- GitHub：[@bryankuok2024](https://github.com/bryankuok2024)

---

**注意：** 本項目仍在開發中。生產環境使用前請進行充分測試和安全評估。 