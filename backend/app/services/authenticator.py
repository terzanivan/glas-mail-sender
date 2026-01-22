import random
from typing import Any
from datetime import datetime, timedelta, timezone
from app.services.pb_service import pb
from app.core.config import settings


class Authenticator:
    @staticmethod
    def generate_code() -> int:
        return random.randint(100000, 999999)

    @staticmethod
    async def create_auth_session(mail_hash: str):
        code = Authenticator.generate_code()
        expiry = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRY_MINUTES
        )

        # Store in PB
        data = {
            "mail_hash": mail_hash,
            "code": code,
            "expiry": expiry.isoformat(),
            "state": "sent",
        }
        return pb.collection("auth_attempts").create(data), code

    @staticmethod
    async def verify_code(mail_hash: str, code: int) -> bool:
        # Fetch the latest attempt for this mail_hash
        try:
            results = pb.collection("auth_attempts").get_list(
                1,
                1,
                {
                    "filter": f'mail_hash = "{mail_hash}" && state = "sent"',
                    "sort": "-created",
                },
            )

            if not results.items:
                return False

            attempt: Any = results.items[0]

            # Check expiry
            expiry_str = attempt.expiry
            expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            if datetime.utcnow() > expiry:
                pb.collection("auth_attempts").update(attempt.id, {"state": "expired"})
                return False

            if attempt.code == code:
                pb.collection("auth_attempts").update(attempt.id, {"state": "success"})
                return True
            else:
                return False
        except Exception:
            return False


authenticator = Authenticator()
