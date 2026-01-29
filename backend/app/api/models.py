from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, HttpUrl
from pydantic_core import Url


class EntityType(str, Enum):
    COMMITTEE = "commission"
    MP = "mp"
    COMPANY = "company"
    GOVERNMENT_ENTITY = "government_entity"


class AuthState(str, Enum):
    SENT = "sent"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"


class PBBaseModel(BaseModel):
    """Base model for PocketBase records"""

    id: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Entity(PBBaseModel):
    name: str
    email: EmailStr
    ent_type: EntityType
    ent_source: str


class TemplateExpand(BaseModel):
    target_entities: List[Entity] = Field(default_factory=list)


class Template(PBBaseModel):
    content: str
    name: str
    target_entities: List[str] = Field(default_factory=list)
    expand: Optional[TemplateExpand] = None


class AuthAttempt(PBBaseModel):
    user_mail_hash: str
    code: int
    expires: datetime
    state: AuthState


class SentLog(PBBaseModel):
    mail_hash: str
    template_id: str
    entity_id: str
    timestamp: datetime


# --- Request Models ---


class OTPRequest(BaseModel):
    name: str
    surname: str
    mail: EmailStr
    template_id: str
    entity_id: str


class VerifyRequest(BaseModel):
    mail: EmailStr
    otp_code: int
    name: str
    surname: str
    template_id: str
    entity_id: str
