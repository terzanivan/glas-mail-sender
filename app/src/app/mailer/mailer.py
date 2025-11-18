import os
import mailtrap as mt
from mailtrap import Mail, Attachment, Address


class Mailer:
    def __init__(self) -> None:
        self.key = os.environ.get("MAILTRAP_API_KEY")
        if self.key is None:
            raise EnvironmentError("missing MAILTRAP_API_KEY")
        self.client = mt.MailtrapClient(token=self.key)

    def send(self, sender: dict, to: list, subject: str, text: str, reply_to: str):
        mail = Mail(
            sender=Address(email=sender["email"], name=sender["name"]),
            to=[
                Address(email=recipient["email"], name=recipient["name"])
                for recipient in to
            ],
            subject=subject,
            text=text,
            reply_to=Address(email=reply_to),
        )

        return self.client.send(mail)
