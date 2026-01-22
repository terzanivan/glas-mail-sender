from pydantic import BaseModel, EmailStr

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
