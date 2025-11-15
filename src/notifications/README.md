# Email Notification Module

邮件通知模块，支持通过163邮箱发送邮件。

## 功能特性

- 支持163邮箱SMTP服务器
- 支持SSL/TLS加密连接
- 支持纯文本和HTML格式邮件
- 支持单发、群发、CC、BCC
- 完整的错误处理和日志记录
- 可通过配置文件初始化

## 使用方法

### 方法1: 直接使用

```python
from src.notifications import EmailNotifier

# 创建邮件通知器实例（使用默认163配置）
notifier = EmailNotifier(
    sender_email="your_email@163.com",
    sender_password="your_authorization_code",
    sender_name="AlphaChain Bot",
    use_ssl=True
)

# 或者指定自定义SMTP服务器（如Gmail）
notifier = EmailNotifier(
    sender_email="your_email@gmail.com",
    sender_password="your_app_password",
    sender_name="AlphaChain Bot",
    smtp_server="smtp.gmail.com",
    smtp_port=465,
    use_ssl=True
)

# 发送纯文本邮件
notifier.send_text_email(
    recipient="recipient@example.com",
    subject="测试邮件",
    text_body="这是一封测试邮件"
)

# 发送HTML邮件
notifier.send_html_email(
    recipient="recipient@example.com",
    subject="HTML邮件",
    html_body="<h1>标题</h1><p>这是HTML内容</p>"
)

# 发送带CC和BCC的邮件
notifier.send_email(
    recipient="recipient@example.com",
    subject="测试邮件",
    body="邮件内容",
    cc=["cc1@example.com", "cc2@example.com"],
    bcc=["bcc@example.com"]
)

# 群发邮件
results = notifier.send_bulk_email(
    recipients=["user1@example.com", "user2@example.com"],
    subject="群发邮件",
    body="邮件内容"
)
```

### 方法2: 从配置文件初始化

```python
from config import settings
from src.notifications import create_email_notifier_from_config

# 从配置创建邮件通知器
notifier = create_email_notifier_from_config(settings)

if notifier:
    notifier.send_text_email(
        recipient="recipient@example.com",
        subject="测试邮件",
        text_body="这是一封测试邮件"
    )
else:
    print("邮件通知未启用或配置错误")
```

## 配置说明

在 `.env` 文件中配置以下参数：

```env
# 启用邮件通知
EMAIL_ENABLED=true

# SMTP服务器地址（支持163、Gmail、QQ等）
EMAIL_SMTP_SERVER=smtp.163.com

# SMTP服务器端口（通常465为SSL，587为TLS，25为非加密）
EMAIL_SMTP_PORT=465

# 发件人邮箱地址
EMAIL_SENDER=your_email@163.com

# 邮箱密码或授权码（163邮箱需要使用授权码）
EMAIL_PASSWORD=your_authorization_code

# 发件人显示名称（可选）
EMAIL_SENDER_NAME=AlphaChain Bot

# 是否使用SSL连接（默认true）
EMAIL_USE_SSL=true
```

### 常用邮件服务商配置

#### 163邮箱

```env
EMAIL_SMTP_SERVER=smtp.163.com
EMAIL_SMTP_PORT=465
EMAIL_USE_SSL=true
```

#### Gmail

```env
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=465
EMAIL_USE_SSL=true
# 或者使用TLS
EMAIL_SMTP_PORT=587
EMAIL_USE_SSL=false
```

#### QQ邮箱

```env
EMAIL_SMTP_SERVER=smtp.qq.com
EMAIL_SMTP_PORT=465
EMAIL_USE_SSL=true
# 或者使用TLS
EMAIL_SMTP_PORT=587
EMAIL_USE_SSL=false
```

#### Outlook/Hotmail

```env
EMAIL_SMTP_SERVER=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587
EMAIL_USE_SSL=false
```

## 163邮箱授权码获取

1. 登录163邮箱
2. 进入"设置" -> "POP3/SMTP/IMAP"
3. 开启SMTP服务
4. 生成授权码（不是登录密码）
5. 将授权码配置到 `EMAIL_PASSWORD`

## 注意事项

- 163邮箱需要使用授权码，而不是登录密码
- 确保已开启SMTP服务
- 建议使用SSL连接（端口465）
- 邮件发送失败会记录到日志中

