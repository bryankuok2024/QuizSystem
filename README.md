# QuizSystem 題庫系統

一個基於 Django 的線上題庫學習系統，支持用戶註冊、題目管理、支付功能和學習進度追蹤。

## 功能特點

### 🎯 核心功能
- **用戶管理** - 用戶註冊、登入、個人資料管理
- **題目管理** - 題目創建、分類、批量導入
- **支付系統** - QR Code 支付、訂閱管理
- **學習進度** - 進度追蹤、統計報告、排行榜

### 🔧 技術特性
- **Django 5.2** - 現代 Python Web 框架
- **MySQL** - 可靠的關聯式數據庫
- **Redis + Celery** - 異步任務處理
- **響應式設計** - 支持多種設備

## 項目結構

```
QuizSystem/
├── quizApp/                 # Django 主項目
│   ├── quizApp/            # 項目設置
│   │   ├── settings.py     # Django 設置
│   │   ├── celery.py       # Celery 配置
│   │   └── urls.py         # URL 路由
│   ├── users/              # 用戶管理應用
│   │   ├── models.py       # 用戶模型
│   │   ├── views.py        # 視圖邏輯
│   │   ├── tasks.py        # 異步任務
│   │   └── urls.py         # 路由配置
│   ├── questions/          # 題目管理應用
│   │   ├── models.py       # 題目模型
│   │   ├── views.py        # 視圖邏輯
│   │   ├── tasks.py        # 異步任務
│   │   └── urls.py         # 路由配置
│   ├── payments/           # 支付系統應用
│   │   ├── models.py       # 支付模型
│   │   ├── views.py        # 視圖邏輯
│   │   ├── tasks.py        # 異步任務
│   │   └── urls.py         # 路由配置
│   ├── progress/           # 學習進度應用
│   │   ├── models.py       # 進度模型
│   │   ├── views.py        # 視圖邏輯
│   │   ├── tasks.py        # 異步任務
│   │   └── urls.py         # 路由配置
│   └── manage.py           # Django 管理腳本
├── venv/                   # Python 虛擬環境
├── requirements.txt        # Python 依賴包
└── README.md              # 項目說明
```

## 安裝與設置

### 環境要求
- Python 3.8+
- MySQL 5.7+
- Redis 5.0+

### 安裝步驟

1. **克隆項目**
   ```bash
   git clone https://github.com/bryankuok2024/QuizSystem.git
   cd QuizSystem
   ```

2. **創建虛擬環境**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # 或
   source venv/bin/activate  # Linux/Mac
   ```

3. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置數據庫**
   
   在 MySQL 中創建數據庫：
   ```sql
   CREATE DATABASE quiz_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. **配置環境變量**
   
   複製並編輯 `quizApp/quizApp/settings.py` 中的數據庫設置：
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'quiz_db',
           'USER': 'your_mysql_user',
           'PASSWORD': 'your_mysql_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

6. **執行數據庫遷移**
   ```bash
   cd quizApp
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **創建超級用戶**
   ```bash
   python manage.py createsuperuser
   ```

## 運行項目

### 啟動 Redis 服務器
```bash
# Windows (下載便攜版 Redis)
.\Redis\redis-server.exe --port 6379

# Linux/Mac
redis-server
```

### 啟動 Celery Worker
```bash
cd quizApp
# Windows
celery -A quizApp worker --loglevel=info --pool=solo

# Linux/Mac
celery -A quizApp worker --loglevel=info
```

### 啟動 Django 開發服務器
```bash
cd quizApp
python manage.py runserver
```

### 啟動 Celery Beat（可選，用於定時任務）
```bash
cd quizApp
celery -A quizApp beat --loglevel=info
```

## 功能模塊

### 用戶管理 (users)
- 用戶註冊與登入
- 個人資料管理
- 郵件通知系統

### 題目管理 (questions)
- 題目創建與編輯
- 分類管理
- 批量導入功能
- 統計報告

### 支付系統 (payments)
- QR Code 支付
- 訂閱管理
- 支付確認
- 自動提醒

### 學習進度 (progress)
- 答題記錄
- 進度統計
- 學習報告
- 排行榜

## 異步任務

系統使用 Celery 處理以下異步任務：
- 郵件發送
- 支付處理
- 進度計算
- 統計報告生成
- 定時任務

## 部署

### 生產環境配置
1. 設置環境變量
2. 配置 Nginx/Apache
3. 使用 Gunicorn 作為 WSGI 服務器
4. 配置 Supervisor 管理 Celery 進程

## 貢獻

歡迎提交 Pull Request 或報告 Issue！

## 授權

本項目採用 MIT 授權條款。

## 聯繫方式

- 作者：Bryan Kuok
- GitHub：[@bryankuok2024](https://github.com/bryankuok2024)

---

**注意：** 本項目為學習目的開發，生產環境使用前請進行充分測試和安全評估。 