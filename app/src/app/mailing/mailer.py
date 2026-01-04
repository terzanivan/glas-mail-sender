from enum import Enum
import os
from typing import TypedDict
import uuid
import mailtrap as mt
from mailtrap import Mail, Address
from pydantic import EmailStr


class MailState(Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    ERROR = "ERROR"
    EXPIRED = "EXPIRED"


class MailConfig(TypedDict):
    sender: Address
    to: list[Address]
    subject: str
    content: str
    reply_to: EmailStr


class Mailer:
    def __init__(self) -> None:
        self.key = os.environ.get("MAILTRAP_API_KEY")
        self.queue: dict[uuid.UUID, Mail] = {}
        if self.key is None:
            raise EnvironmentError("missing MAILTRAP_API_KEY")
        self.client = mt.MailtrapClient(token=self.key)

    def send(self, mail_id: uuid.UUID):
        mail = self.queue.get(mail_id)
        if mail is None:
            raise KeyError(f"{mail_id} not found")
        self.client.send(mail)

    def prepare(self, mailCfg: MailConfig) -> tuple[uuid.UUID, Mail]:
        mail = Mail(
            sender=Address(email=mailCfg["sender"].email, name=mailCfg["sender"].name),
            to=[
                Address(email=recipient.email, name=recipient.name)
                for recipient in mailCfg["to"]
            ],
            subject=mailCfg["subject"],
            text=mailCfg["content"],
            reply_to=Address(email=mailCfg["reply_to"]),
        )
        mail_id = uuid.UUID()

        return mail_id, mail
