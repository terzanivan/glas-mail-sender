from pydantic import BaseModel, EmailStr

class MailRequest(BaseModel):
    name: str
    surname: str
    mail: EmailStr
    selected_template: int
    selected_entity: int

class Template(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Entity(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
