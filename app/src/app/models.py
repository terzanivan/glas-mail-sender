from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime

template_entity_association = Table(
    'template_entity_association',
    Base.metadata,
    Column('template_id', Integer, ForeignKey('templates.id')),
    Column('entity_id', Integer, ForeignKey('entities.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email_hash = Column(String, unique=True, index=True)
    last_sent_at = Column(DateTime(timezone=True), server_default=func.now())

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    content = Column(String)
    entities = relationship("Entity", secondary=template_entity_association, back_populates="templates")

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    templates = relationship("Template", secondary=template_entity_association, back_populates="entities")

class SentMail(Base):
    __tablename__ = "sent_mails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, ForeignKey("templates.id"))
    entity_id = Column(Integer, ForeignKey("entities.id"))
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    template = relationship("Template")
    entity = relationship("Entity")
