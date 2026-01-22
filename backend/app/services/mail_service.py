from typing import Optional
import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

class MailSender:
    @staticmethod
    async def send_mail(to_email: str, subject: str, content: str, reply_to: Optional[str] = None):
        message = EmailMessage()
        domain: str = settings.DOMAIN_NAME or "example.com"
        from_addr = f"Glas Mailer <no-reply@{domain}>"
        message["From"] = from_addr
        message["To"] = to_email
        message["Subject"] = subject
        if reply_to:
            message["Reply-To"] = reply_to
        message.set_content(content)

        await aiosmtplib.send(
            message,
            hostname=settings.MAILTRAP_HOST,
            port=settings.MAILTRAP_PORT,
            username=settings.MAILTRAP_USER,
            password=settings.MAILTRAP_PASSWORD,
            use_tls=False, # Mailtrap usually uses STARTTLS or none
        )

mail_sender = MailSender()
