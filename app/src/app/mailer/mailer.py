import os
import mailtrap


class Mailer:
    def __init__(self) -> None:
        self.key = os.environ.get("MAILTRAP_API_KEY")
        pass
