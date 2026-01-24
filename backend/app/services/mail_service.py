from ast import Add
from typing import Optional
import aiosmtplib
from mailtrap import (
    Address,
    ClientConfigurationError,
    MailtrapClient,
    Mail,
    MailtrapError,
)
from app.core.config import settings

token = settings.MAILTRAP_TOKEN
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
