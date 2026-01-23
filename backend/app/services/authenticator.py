import random
from typing import Tuple
from datetime import datetime, timedelta, timezone
from app.services.pb_service import pb
from app.core.config import settings
from app.api.models import AuthAttempt, AuthState


class Authenticator:
    @staticmethod
    def generate_code() -> int:
        return random.randint(100000, 999999)

    @staticmethod
    async def create_auth_session(mail_hash: str) -> Tuple[AuthAttempt, int]:
        code = Authenticator.generate_code()
        expiry = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRY_MINUTES
        )

        # Store in PB
        data = {
            "mail_hash": mail_hash,
            "code": code,
            "expiry": expiry.isoformat(),
            "state": AuthState.SENT,
        }
        record = pb.collection("auth_attempts").create(data)
        return AuthAttempt.model_validate(record), code

    @staticmethod
    async def verify_code(mail_hash: str, code: int) -> bool:
        # Fetch the latest attempt for this mail_hash
        try:
            results = pb.collection("auth_attempts").get_list(
                1,
                1,
                {
                    "filter": f'mail_hash = "{mail_hash}" && state = "{AuthState.SENT}"',
                    "sort": "-created",
                },
            )

            if not results.items:
                return False

            attempt_record = results.items[0]
            attempt = AuthAttempt.model_validate(attempt_record)

            # Check expiry
            if datetime.now(timezone.utc) > attempt.expiry:
                pb.collection("auth_attempts").update(
                    attempt.id, {"state": AuthState.EXPIRED}
                )
                return False

            if attempt.code == code:
                pb.collection("auth_attempts").update(
                    attempt.id, {"state": AuthState.SUCCESS}
                )
                return True
            else:
                return False
        except Exception:
            return False


authenticator = Authenticator()
