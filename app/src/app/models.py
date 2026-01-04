import hashlib
import json
import os
from typing import override
import uuid
from pydantic_core import PydanticCustomError
from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, validates, mapped_column
from sqlalchemy.sql import func

from app.mailing.mailer import MailState
from .database import Base
from pydantic import ValidationError, validate_email

# template_entity_association = Table(
#     "template_entity_association",
#     Base.metadata,
#     Column("template_id", Integer, ForeignKey("templates.id")),
#     Column("entity_id", Integer, ForeignKey("entities.id")),
# )

VALID_DOMAINS = (
    []
    if os.environ.get("VALID_DOMAINS") is None
    else json.loads(
        os.environ.get("VALID_DOMAINS")  # pyright: ignore[reportArgumentType]
    )
)


class UnsupportedDomain(Exception):
    def __init__(self, domain: str) -> None:
        super().__init__(domain)
        self.domain = domain

    @override
    def __str__(self) -> str:
        return f"domain {self.domain} is not supported by this platform"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email_hash: Mapped[str] = mapped_column(unique=True, index=True)
    last_sent_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    @staticmethod
    def hash_email(email: str, salt: str = "glas") -> str:
        email = salt + email
        return hashlib.sha256(email.encode()).hexdigest()

    @validates("email")
    def validate_user_email(self, key: str, email: str, salt: str = "glas") -> str:
        """Validates the user email and returns a hash of it for storing in the database"""
        if type(email) is not str:
            raise TypeError(f"Bad email value: {email}")

        try:
            validate_email(email)
        except PydanticCustomError:
            raise ValidationError(f"invalid {key} provided for MP {email}")
        domain = email.split("@")[1]

        if domain not in VALID_DOMAINS:
            raise UnsupportedDomain(domain)
        return self.hash_email(email, salt)


class ParliamentGroup(Base):
    __tablename__ = "parliament_group"
    id: Mapped[int] = mapped_column(index=True, autoincrement="auto")
    name: Mapped[str] = mapped_column()


class ElectorateArea(Base):
    __tablename__ = "electorate_area"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement="auto")
    name: Mapped[str] = mapped_column()


class MP(Base):
    __tablename__ = "parliament_members"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement="auto")
    name: Mapped[str] = mapped_column(primary_key=True, unique=True)
    email: Mapped[str] = mapped_column()
    parliament_group_id: Mapped[int] = mapped_column(ForeignKey("parliament_group.id"))
    electorate_area: Mapped[int] = mapped_column(ForeignKey("electorate_area.id"))
    template_id: Mapped[int] = mapped_column(ForeignKey("template.id"))

    @validates("name")
    def validate_mp_name(self, key: str, value: str):
        if type(value) is not str:
            raise TypeError(f"Bad mp_name value: {value}")
        if len(value.split(" ")) != 3:
            raise ValidationError(
                f"{key} should consist of name, surname, and family name: {value}"
            )


class Template(Base):
    __tablename__ = "template"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    content: Mapped[str] = mapped_column()


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column()
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"))


class Mails(Base):
    __tablename__ = "mails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"))
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    sent_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    state: Mapped[MailState] = mapped_column(Enum(MailState))


# TODO: Send email request verification
class VerificationsRequests(Base):
    __tablename__ = "verification_requests"

    id: Mapped[str] = mapped_column(default=uuid.UUID().__str__())
    user: Mapped[str] = mapped_column(ForeignKey("user.id"))
    sent: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    expires: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
