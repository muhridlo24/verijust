from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from typing import List

# 1. Define conf as None initially
conf = None

# 2. Only initialize the config if credentials exist in .env
# This prevents the ValidationError crash on startup
if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

async def send_email(
    email_to: List[str], 
    subject: str, 
    html_content: str
) -> bool:
    """
    Safely sends an email. If no credentials are set, it just prints to console.
    """
    # 3. Check if config exists before trying to send
    if not conf:
        print(f"⚠️ [Email Service] Skipped email to {email_to[0]}: No credentials in .env")
        return False

    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    
    try:
        await fm.send_message(message)
        print(f"✅ [Email Service] Email sent to {email_to}")
        return True
    except Exception as e:
        print(f"❌ [Email Service] Failed: {e}")
        return False