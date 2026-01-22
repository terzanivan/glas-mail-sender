import hashlib
from app.core.config import settings

def hash_email(email: str) -> str:
    """Hashes the email with a salt for privacy and abuse prevention."""
    salted_email = f"{email}{settings.MAIL_HASH_SALT}"
    return hashlib.sha256(salted_email.encode()).hexdigest()
