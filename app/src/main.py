from typing import TypedDict
import itsdangerous
from mailtrap import Address
from .app.mailing.mailer import MailConfig, Mailer
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .app import models, schemas, database
from .app.database import engine
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta, timezone
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
mailer = Mailer()

SECRET_KEY = os.getenv("SECRET_KEY")
SALT = os.getenv("GLAS_SALT")
if SECRET_KEY is None:
    raise EnvironmentError("missing SEC")
serializer = URLSafeTimedSerializer(SECRET_KEY)


class VerificationToken(TypedDict):
    user_id: int
    name: str
    surname: str
    mail: str
    template_id: int
    entity_id: int


@app.post("/mails/request")
def request_mail(
    request: schemas.MailRequest,
    http_request: Request,
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .filter(
            models.User.email_hash
            == models.User.hash_mail(email=request.mail, salt=SALT)
        )
        .first()
    )

    # INFO: If the user exists in the database, make sure he hasn't send a mail in the last 72 hours
    if user:
        # Check for 72-hour limit
        if user.last_sent_at > datetime.now(timezone.utc) - timedelta(hours=72):
            raise HTTPException(
                status_code=429, detail="You can only send one mail every 72 hours."
            )

        # Check for duplicate template-entity for the same user
        existing_sent_mail = (
            db.query(models.Mails)
            .filter(
                models.Mails.user_id == user.id,
                models.Mails.template_id == request.selected_template,
                models.Mails.entity_id == request.selected_entity,
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
    token_data = VerificationToken(
        user_id=user.id,
        name=request.name,
        surname=request.surname,
        mail=request.mail,
        template_id=request.selected_template,
        entity_id=request.selected_entity,
    )
    token = serializer.dumps(token_data)

    """ NOTE: 
    tag:email-verification

    Email verification happens as follows:
    - we generate a verification token (above) (VT)
    - send VT to the user-provided email as a clickable link
    """

    verification_link = http_request.url_for("verify_user_email", token=token)
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
    http_request.session["mail_id"] = mail_id

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


""" NOTE: 
tag:email-verification

Email verification happens as follows:

- receive token input from url in previuosly sent mail
- check the validity of the token input
- return the response to the frontend in order to continue the mail sending process
"""


@app.post("/mails/verify/{token}", name="verify_user_email")
def verify_mail_request(http_request: Request, token: str):
    mail_id = http_request.session["mail_id"]
    if not mail_id:
        raise HTTPException(status_code=400, detail="No mail_id provided")
    if not token:
        raise HTTPException(status_code=400, detail="No token provided")

    try:
        mailer.queue[mail_id]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid mail_id provided")
    try:
        decoded_token: dict = serializer.loads(token, max_age=3600)
        verified_token = VerificationToken(**decoded_token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    return {"message": "Verification successful.", "user_id": verified_token["user_id"]}


@app.post("/mails/send")
def send_mail(
    request: schemas.MailRequest,
    http_request: Request,
    db: Session = Depends(database.get_db),
):
    print("We sent the mail")
    print("Mail content:{content}")
    pass


# TODO: Token verification logic


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
