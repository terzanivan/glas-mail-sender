from mailtrap.models.mail import Mail


class MailingObserver:
    def __init__(self) -> None:
        self.pendingMails: dict[int, Mail] = {}
        pass
