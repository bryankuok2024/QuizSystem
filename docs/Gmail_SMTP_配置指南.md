# Gmail SMTP 配置指南

## 🎯 目標
在 Django 項目 QUIZSYSTEM 中配置 Gmail SMTP，支援：
- ✅ 用戶註冊郵件驗證 (如果 `ACCOUNT_EMAIL_VERIFICATION` 設為 `mandatory` 或 `optional`)
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
   - 選擇應用: 「郵件」
   - 選擇裝置: 「Windows 電腦」(或其他合適的選項)
   - 複製生成的 16 字符密碼（例如：`abcd efgh ijkl mnop`）。**注意：此密碼不應包含空格，Google 生成時可能帶有空格以便閱讀，但使用時應移除。**

## 🔧 配置步驟

### 1. 編輯環境變量文件
在項目根目錄 (`QUIZSYSTEM/`) 下的 `.env` 文件中添加或修改以下行：

```dotenv
# Gmail SMTP 配置
USE_GMAIL_SMTP=True
EMAIL_HOST_USER='your_actual_gmail_address@gmail.com'
EMAIL_HOST_PASSWORD='your_16_character_app_password_no_spaces'
DEFAULT_FROM_EMAIL='題庫系統 <your_actual_gmail_address@gmail.com>'

# 可選，如果settings.py中使用 generic SMTP 且 USE_GMAIL_SMTP=True 但非gmail.com郵箱
# EMAIL_HOST='smtp.gmail.com'
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_USE_SSL=False
```

### 2. 替換實際數值
- `your_actual_gmail_address@gmail.com`：您的 Gmail 地址。
- `your_16_character_app_password_no_spaces`：您從 Google 生成的16字符應用程式密碼 (移除所有空格)。
- `題庫系統 <your_actual_gmail_address@gmail.com>`：作為郵件寄件人顯示的名稱和郵箱。

### 3. 確保 `.env` 文件安全
`.env` 文件通常已在項目的 `.gitignore` 文件中，以防止提交到版本控制系統。如果沒有，請添加它：
```bash
echo ".env" >> .gitignore
```

## 📁 文件結構 (相關部分)
```
QUIZSYSTEM/
├── .env                    # 環境變量 (包含 Gmail SMTP 配置)
├── .gitignore
├── manage.py
├── core_settings/
│   └── settings.py         # 從 .env 加載郵件配置
└── ... (其他項目文件)
```

## ⚙️ 配置詳情 (`core_settings/settings.py` 中的相關邏輯)
```python
# (已在 settings.py 頂部加載 .env 文件)
# from dotenv import load_dotenv
# load_dotenv()

# 從環境變量中讀取最終要使用的郵件配置
FINAL_USE_GMAIL_SMTP = os.getenv('USE_GMAIL_SMTP', 'False').lower() == 'true'
FINAL_EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
FINAL_EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
FINAL_DEFAULT_FROM_EMAIL_ENV = os.getenv('DEFAULT_FROM_EMAIL', '')

if FINAL_USE_GMAIL_SMTP and FINAL_EMAIL_HOST_USER and FINAL_EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    
    # 檢測郵件服務商並設置相應的 SMTP 配置 (主要針對 Gmail)
    if '@gmail.com' in FINAL_EMAIL_HOST_USER or '@yenoo.co' in FINAL_EMAIL_HOST_USER: # yenoo.co 是示例
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_USE_SSL = False
    else:
        # 如果不是 Gmail，但仍然要求使用 SMTP，則使用通用的環境變量
        EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com') 
        EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
        EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
        EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'

    EMAIL_HOST_USER = FINAL_EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = FINAL_EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = FINAL_DEFAULT_FROM_EMAIL_ENV if FINAL_DEFAULT_FROM_EMAIL_ENV else f'QuizSystem <{FINAL_EMAIL_HOST_USER}>'
    SERVER_EMAIL = FINAL_EMAIL_HOST_USER  # 用於伺服器錯誤通知
    EMAIL_TIMEOUT = 60 # 連接超時時間 (秒)
    # EMAIL_USE_LOCALTIME = False (如果需要)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # 開發時打印到控制台
    DEFAULT_FROM_EMAIL = 'QuizSystem Console <noreply@quizsystem.dev>'
    # 清理 SMTP 相關變量
    EMAIL_HOST_USER = None
    EMAIL_HOST_PASSWORD = None
    # ... 其他 SMTP 變量可以設為 None 或默認值

EMAIL_SUBJECT_PREFIX = '[題庫系統] ' # 所有郵件主題的前綴
```

### 關鍵設置說明
- **`USE_GMAIL_SMTP`**: `.env` 中的布爾值，決定是否啟用 SMTP。
- **`EMAIL_HOST`**: 對於 Gmail 是 `smtp.gmail.com`。
- **`EMAIL_PORT`**: 對於 Gmail (TLS) 是 `587`。
- **`EMAIL_USE_TLS`**: 對於 Gmail 是 `True`。
- **`EMAIL_HOST_USER`**: 你的 Gmail 郵箱地址 (從 `.env` 加載)。
- **`EMAIL_HOST_PASSWORD`**: 你的 Gmail 應用密碼 (從 `.env` 加載)。
- **`DEFAULT_FROM_EMAIL`**: 郵件中顯示的發件人 (從 `.env` 加載)。

## 🧪 測試配置

確保 `.env` 文件中 `USE_GMAIL_SMTP=True` 並且相關憑證已正確設置。

### 1. 使用 Django Shell 檢查設置和發送測試郵件
在項目根目錄 (`QUIZSYSTEM/`) 運行:
```bash
python manage.py shell
```

然後在 Shell 中執行:
```python
from django.conf import settings
from django.core.mail import send_mail
import os

print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER (from settings): {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# 確認環境變量是否正確加載 (用於調試)
# print(f"EMAIL_HOST_USER (from os.getenv direct): {os.getenv('EMAIL_HOST_USER')}")
# print(f"EMAIL_HOST_PASSWORD is set: {'Yes' if os.getenv('EMAIL_HOST_PASSWORD') else 'No'}")

# 發送測試郵件
if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    try:
        send_mail(
            subject=f'{settings.EMAIL_SUBJECT_PREFIX} Django SMTP 測試郵件',
            message='這是一封通過 Gmail SMTP 從您的 Django QuizSystem 應用發送的測試郵件。',
            from_email=settings.DEFAULT_FROM_EMAIL, # 或者直接指定 settings.EMAIL_HOST_USER
            recipient_list=['your_personal_test_email@example.com'], # 替換為你的測試郵箱
            fail_silently=False,
        )
        print("測試郵件已嘗試發送。請檢查您的收件箱和垃圾郵件文件夾。")
    except Exception as e:
        print(f"郵件發送失敗: {e}")
else:
    print("郵件後端未配置為 SMTP，郵件將打印到控制台 (如果通過 console backend 發送)。")
    # 如果是 console backend，可以這樣觸發打印:
    # send_mail('Console Test', 'This is a test.', 'console@example.com', ['recipient@example.com'])

exit()
```
將 `your_personal_test_email@example.com` 替換為你實際可以接收郵件的地址。

### 2. 測試 allauth 功能 (如果郵件驗證已啟用)
1.  訪問註冊頁面：`http://127.0.0.1:8000/accounts/signup/`
2.  使用一個新的郵箱地址註冊用戶。
3.  如果 `ACCOUNT_EMAIL_VERIFICATION` 設置為 `mandatory` 或 `optional`，檢查該郵箱是否收到驗證郵件。
4.  嘗試密碼重置功能，看是否收到密碼重置郵件。

## 🚀 使用方式

### 開發環境
在 `.env` 文件中設置 `USE_GMAIL_SMTP=False` (或註釋掉/移除該行以及 `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`)。系統將使用 `django.core.mail.backends.console.EmailBackend`，郵件內容會打印到運行 `runserver` 的終端。

### 生產環境
在 `.env` 文件中設置 `USE_GMAIL_SMTP=True` 並提供正確的 Gmail 憑證。

## 🔒 安全建議

1.  **絕對不要在代碼中硬編碼敏感憑證 (如密碼)。** 始終使用環境變量。
2.  **確保 `.env` 文件已添加到 `.gitignore**，防止其被提交到版本控制系統。
3.  **定期更換您的 Google 應用程式密碼**，尤其是在懷疑洩露時。
4.  在生產環境中，考慮使用更安全的機密管理服務 (如 HashiCorp Vault, AWS Secrets Manager, Google Cloud Secret Manager) 而不是僅僅依賴 `.env` 文件，儘管 `.env` 對於許多場景已經足夠。

## 📧 支援的郵件功能 (通過 allauth 和 Django)

### django-allauth (根據配置)
- ✅ 註冊驗證郵件
- ✅ 密碼重置郵件
- ✅ 郵箱地址更改確認郵件

### 自定義郵件 (使用 Django 的 `send_mail`)
```python
from django.core.mail import send_mail
from django.conf import settings

# 示例：發送通知郵件
# send_mail(
#     subject=f'{settings.EMAIL_SUBJECT_PREFIX} 您的測驗成績已發佈',
#     message='尊敬的用戶，您的最新測驗成績已發佈，請登錄查看。',
#     from_email=settings.DEFAULT_FROM_EMAIL,
#     recipient_list=[user_email_address], # 目標用戶的郵箱地址
#     fail_silently=False, # 如果發送失敗則拋出異常
# )
```

## 🐛 常見問題及解決方案

### 1. `smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted...')`
   - **原因**: Gmail 應用密碼不正確或已失效，或者 Gmail 帳戶的安全設置阻止了登錄。
   - **解決方案**:
     *   仔細檢查 `.env` 中的 `EMAIL_HOST_USER` 和 `EMAIL_HOST_PASSWORD` 是否完全正確 (密碼無空格，郵箱地址正確)。
     *   重新生成一個新的 Google 應用程式密碼並更新到 `.env` 文件。
     *   檢查 Google 帳戶是否有任何安全警報，可能需要確認可疑活動。
     *   極少數情況下，Google 可能臨時鎖定不常見的登錄嘗試。等待一段時間再試。

### 2. 郵件發送失敗 (無明顯錯誤，或 `TimeoutError`)
   - **原因**: 防火牆阻止了到 `smtp.gmail.com:587` 的出站連接；網絡不穩定；`EMAIL_TIMEOUT` 太短。
   - **解決方案**:
     *   檢查本地和網絡防火牆設置，確保允許到 `smtp.gmail.com` 的 TCP 端口 `587` 的出站連接。
     *   嘗試增加 `settings.py` 中的 `EMAIL_TIMEOUT` 值 (例如，改為 `120`)。

### 3. 收不到郵件
   - **原因**: 郵件被歸類為垃圾郵件；收件人郵箱地址錯誤；Gmail 的發送配額限制。
   - **解決方案**:
     *   檢查收件箱的垃圾郵件 (Spam) 文件夾。
     *   仔細核對測試時使用的收件人郵箱地址是否正確無誤。
     *   注意 Gmail 對於通過 SMTP 大量發送郵件有限制。對於大量郵件，應考慮使用專門的郵件服務 (如 SendGrid, Mailgun 等)。

### 4. `[WinError 10060] A connection attempt failed...` 或類似連接超時
   - **原因**: 與問題2類似，通常是網絡或防火牆問題。
   - **解決方案**: 參考問題2的解決方案。

## 📊 監控和日誌

- 查看 Django 應用日誌 (在 `logs/django.log` 或控制台，取決於日誌配置) 中是否有關於郵件發送的錯誤或信息。
- 在 `settings.py` 中臨時啟用更詳細的 Django 日誌級別可能會有幫助：
  ```python
  # LOGGING = { ... 'handlers': { 'console': { 'level': 'DEBUG' ... } } ... }
  ```

## 🎉 完成！

正確配置後，您的 Django QuizSystem 應用程序將能夠通過 Gmail SMTP 可靠地發送郵件。 