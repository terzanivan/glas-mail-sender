from typing import Optional
import aiosmtplib
from email.message import EmailMessage
from mailtrap import (
    Address,
    ClientConfigurationError,
    MailtrapClient,
    Mail,
    MailtrapError,
)
from app.core.config import settings

# Initialize Mailtrap client only if needed
client = None
if not settings.USE_LOCAL_MAIL:
    token = settings.MAILTRAP_API_TOKEN
    if not token:
        raise ClientConfigurationError("no mailtrap token provided")
    client = MailtrapClient(token=token)


class MailSender:
    @staticmethod
    async def send_mail(
        to_email: list[str],
        sender: str,
        subject: str,
        content: str,
        reply_to: Optional[str] = None,
    ):
        if settings.USE_LOCAL_MAIL:
            await MailSender._send_local(to_email, sender, subject, content, reply_to)
        else:
            await MailSender._send_mailtrap(to_email, sender, subject, content, reply_to)

    @staticmethod
    async def _send_local(
        to_email: list[str],
        sender: str,
        subject: str,
        content: str,
        reply_to: Optional[str] = None,
    ):
        message = EmailMessage()
        message["From"] = sender
        message["To"] = ", ".join(to_email)
        message["Subject"] = subject
        if reply_to:
            message["Reply-To"] = reply_to
        message.set_content(content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.LOCAL_SMTP_HOST,
            port=settings.LOCAL_SMTP_PORT,
        )

    @staticmethod
    async def _send_mailtrap(
        to_email: list[str],
        sender: str,
        subject: str,
        content: str,
        reply_to: Optional[str] = None,
    ):
        if client is None:
            raise ClientConfigurationError("Mailtrap client not initialized")
            
        receivers = [Address(email=receiver) for receiver in to_email]
        message = Mail(
            to=receivers,
            sender=Address(email=sender),
            reply_to=Address(email=reply_to) if reply_to is not None else None,
            subject=subject,
            html=content,
        )
        result = client.send(message)
        if not result["success"]:
            raise MailtrapError(result)


mail_sender = MailSender()
