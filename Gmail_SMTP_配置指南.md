# Gmail SMTP 配置指南

## 🎯 目標
在 Django 項目 quizApp 中配置 Gmail SMTP，支援：
- ✅ 用戶註冊郵件驗證
- ✅ 密碼重置郵件
- ✅ 其他系統通知郵件

## 📋 前置條件

### 1. Gmail 帳戶設置
1. **啟用 2 步驟驗證**
   - 進入 [Google 帳戶設置](https://myaccount.google.com/)
   - 點擊「安全性」
   - 啟用「2 步驟驗證」

2. **生成應用程式密碼**
   - 在「安全性」頁面找到「應用程式密碼」
   - 選擇「郵件」和「Windows 電腦」
   - 複製生成的 16 字符密碼（例如：`abcd efgh ijkl mnop`）

## 🔧 配置步驟

### 1. 創建環境變量文件
在項目根目錄（`QuizSystem/quizApp/`）創建 `.env` 文件：

```bash
# Gmail SMTP 配置
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=題庫系統 <your_email@gmail.com>
USE_GMAIL_SMTP=True
```

### 2. 替換實際數值
- `your_email@gmail.com`：您的 Gmail 地址
- `abcd efgh ijkl mnop`：Gmail 應用程式密碼（16 字符，包含空格）
- `題庫系統 <your_email@gmail.com>`：郵件寄件人顯示名稱

### 3. 確保文件安全
將 `.env` 添加到 `.gitignore`：
```bash
echo ".env" >> .gitignore
```

## 📁 文件結構
```
QuizSystem/
├── quizApp/
│   ├── .env                    # 環境變量（需要創建）
│   ├── .env.example           # 環境變量示例
│   ├── manage.py
│   ├── quizApp/
│   │   └── settings.py        # 已更新 Gmail SMTP 配置
│   └── ...
└── ...
```

## ⚙️ 配置詳情

### settings.py 中的配置
```python
# 郵件設置
USE_GMAIL_SMTP = os.getenv('USE_GMAIL_SMTP', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

if USE_GMAIL_SMTP and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    # Gmail SMTP 配置
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_HOST_USER = EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'題庫系統 <{EMAIL_HOST_USER}>')
    SERVER_EMAIL = EMAIL_HOST_USER
    EMAIL_TIMEOUT = 60
```

### 關鍵設置說明
- **EMAIL_HOST**: `smtp.gmail.com` - Gmail SMTP 伺服器
- **EMAIL_PORT**: `587` - SMTP 端口
- **EMAIL_USE_TLS**: `True` - 啟用 TLS 加密
- **EMAIL_TIMEOUT**: `60` - 連接超時時間

## 🧪 測試配置

### 1. 檢查設置
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# 檢查郵件後端
print(f"郵件後端: {settings.EMAIL_BACKEND}")
print(f"SMTP 主機: {settings.EMAIL_HOST}")
print(f"寄件人: {settings.DEFAULT_FROM_EMAIL}")
```

### 2. 發送測試郵件
```python
send_mail(
    subject='測試郵件',
    message='這是一封來自題庫系統的測試郵件。',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your_test_email@example.com'],
    fail_silently=False,
)
```

### 3. 測試 allauth 功能
1. 訪問註冊頁面：http://127.0.0.1:8000/accounts/signup/
2. 填寫註冊表單
3. 檢查郵箱是否收到驗證郵件

## 🚀 使用方式

### 開發環境
設置 `USE_GMAIL_SMTP=False` 或不設置，系統將使用控制台後端：
```bash
USE_GMAIL_SMTP=False
```

### 生產環境
設置 `USE_GMAIL_SMTP=True` 啟用 Gmail SMTP：
```bash
USE_GMAIL_SMTP=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## 🔒 安全建議

1. **從不在代碼中硬編碼密碼**
2. **將 .env 添加到 .gitignore**
3. **定期更換應用程式密碼**
4. **生產環境使用環境變量或機密管理服務**

## 📧 支援的郵件功能

### django-allauth
- ✅ 註冊驗證郵件
- ✅ 密碼重置郵件
- ✅ 郵箱更改確認
- ✅ 登入通知（可選）

### 自定義郵件
```python
from django.core.mail import send_mail

send_mail(
    subject='題庫系統通知',
    message='您的測驗成績已發佈',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[user.email],
)
```

## 🐛 常見問題

### 1. 郵件發送失敗
- 檢查 Gmail 應用程式密碼是否正確
- 確認 2 步驟驗證已啟用
- 檢查網路連接

### 2. 收不到郵件
- 檢查垃圾郵件夾
- 確認收件人郵箱地址正確
- 檢查 Gmail 發送限制

### 3. 連接超時
- 檢查防火牆設置
- 確認 587 端口開放
- 嘗試增加 EMAIL_TIMEOUT 值

## 📊 監控和日誌

查看郵件發送日誌：
```bash
tail -f logs/django.log | grep -i email
```

檢查 Django 郵件設置：
```python
python manage.py shell -c "from django.conf import settings; print(settings.EMAIL_BACKEND)"
```

## 🎉 完成！

配置完成後，您的 Django 應用將能夠：
- 📧 發送註冊驗證郵件
- 🔐 發送密碼重置郵件
- 📬 發送其他系統通知

現在就可以測試 django-allauth 的郵件功能了！ 