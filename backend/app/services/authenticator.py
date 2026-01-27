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
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.OTP_EXPIRY_MINUTES
        )

        # Store in PB
        data = {
            "user_mail_hash": mail_hash,
            "code": code,
            "expires": expires.isoformat(),
            "state": AuthState.SENT,
        }
        record = pb.collection("auth_attempt").create(data)
        return AuthAttempt.model_validate(record), code

    @staticmethod
    async def verify_code(mail_hash: str, code: int) -> bool:
        # Fetch the latest attempt for this mail_hash
        try:
            results = pb.collection("auth_attempt").get_list(
                1,
                1,
                query_params={
                    "filter": f'user_mail_hash = "{mail_hash}" && state = "{AuthState.SENT.value}"',
                    "sort": "-created",
                },
            )

            if not results.items:
                print("could not fetch any codes")
                return False

            attempt_record = results.items[0]
            attempt = AuthAttempt.model_validate(attempt_record)

            # Check expiry
            if datetime.now(timezone.utc) > attempt.expires:
                print(f"code is expred :{attempt.code} expected: {code}")
                pb.collection("auth_attempt").update(
                    attempt.id,  # pyright: ignore[reportArgumentType]
                    {"state": AuthState.EXPIRED},
                )
                return False

            if attempt.code == code:
                pb.collection("auth_attempt").update(
                    attempt.id,  # pyright: ignore[reportArgumentType]
                    {"state": AuthState.SUCCESS},
                )
                return True
            else:
                print(f"codes do not match received:{attempt.code} expected: {code}")
                return False
        except Exception as e:
            raise e


authenticator = Authenticator()
