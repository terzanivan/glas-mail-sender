from email.policy import HTTP
from re import sub
from mailtrap import Address
from .app.mailer.prepare import prepare_mail
from .app.mailer.mailer import MailConfig, Mailer
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .app import models, schemas, database
from .app.database import engine
import hashlib
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta, timezone
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
mailer = Mailer()

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise EnvironmentError("missing SEC")
serializer = URLSafeTimedSerializer(SECRET_KEY)


@app.post("/send-mail")
def send_mail(
    request: schemas.MailRequest,
    http_request: Request,
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email_hash == models.User.hash_mail(request.mail))
        .first()
    )

    if user:
        # Check for 72-hour limit
        if user.last_sent_at > datetime.now(timezone.utc) - timedelta(hours=72):
            raise HTTPException(
                status_code=429, detail="You can only send one mail every 72 hours."
            )

        # Check for duplicate template-entity for the same user
        existing_sent_mail = (
            db.query(models.SentMail)
            .filter(
                models.SentMail.user_id == user.id,
                models.SentMail.template_id == request.selected_template,
                models.SentMail.entity_id == request.selected_entity,
            )
            .first()
        )
        if existing_sent_mail:
            raise HTTPException(
                status_code=409,
                detail="You have already sent this template to this entity.",
            )

    # If user does not exist, create one
    if not user:
        user = models.User(email_hash=request.mail)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate verification token
    token_data = {
        "user_id": user.id,
        "name": request.name,
        "surname": request.surname,
        "mail": request.mail,
        "template_id": request.selected_template,
        "entity_id": request.selected_entity,
    }
    token = serializer.dumps(token_data)

    verification_link = http_request.url_for("verify_email", token=token)
    user = db.query(models.User).filter(models.User.id == user.id).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid user")
    template = (
        db.query(models.Template)
        .filter(models.Template.id == token_data["template_id"])
        .first()
    )
    if template is None:
        raise HTTPException(status_code=400, detail="Invalid template")
    entity = (
        db.query(models.Entity)
        .filter(models.Entity.id == token_data["entity_id"])
        .first()
    )
    if entity is None:
        raise HTTPException(status_code=400, detail="Invalid entity")

    # TODO: Put the mail_id in a session so that it's returned by the frontend later
    mail_id, mail = mailer.prepare(
        mailCfg=MailConfig(
            sender=Address(
                email=request.name + "." + request.surname + ".@glasnarodenbg.eu",
                name=f"{token_data['name']} {token_data["surname"]}",
            ),
            to=[Address(email=entity.email, name=entity.name)],
            subject=template.name,
            content="",
            reply_to=token_data["email"],
        )
    )

    return {
        "message": "Verification link generated. Please check your email.",
        "verification_link": verification_link,
        "mail": {
            "sender": mail.sender,
            "reply_to": mail.reply_to,
            "subject": mail.subject,
            "content": mail.text,
        },
        "mail_id": mail_id,
    }


# TODO: Token verification logic
@app.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(database.get_db)):
    try:
        token_data = serializer.loads(token, max_age=3600)  # Token valid for 1 hour
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    # Record the sent mail and update user timestamp
    # sent_mail = models.SentMail(
    #     user_id=user.id,  # pyright: ignore[]
    #     template_id=template.id,  # pyright: ignore[]
    #     entity_id=entity.id,  # pyright: ignore[]
    # )
    # db.add(sent_mail)
    # user.last_sent_at = datetime.now(timezone.utc)  # pyright: ignore[]
    # db.commit()

    return {"message": "Email verified and mail sent successfully!"}


@app.get("/templates", response_model=list[schemas.Template])
def get_templates(db: Session = Depends(database.get_db)):
    templates = db.query(models.Template).all()
    return templates


@app.get("/entities/{template_id}", response_model=list[schemas.Entity])
def get_entities(template_id: int, db: Session = Depends(database.get_db)):
    template = (
        db.query(models.Template).filter(models.Template.id == template_id).first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template.entities


@app.get("/")
def read_root():
    return {"Hello": "World"}
