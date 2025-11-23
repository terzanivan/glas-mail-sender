from .app.mailer.prepare import prepare_mail
from .app.mailer.mailer import Mailer
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

    user = db.query(models.User).filter(models.User.email_hash == request.mail).first()

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

    # TODO: Send email with verification_link

    return {
        "message": "Verification link generated. Please check your email.",
        "verification_link": verification_link,
    }


@app.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(database.get_db)):
    try:
        token_data = serializer.loads(token, max_age=3600)  # Token valid for 1 hour
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    user_id = token_data["user_id"]
    template_id = token_data["template_id"]
    entity_id = token_data["entity_id"]

    user = db.query(models.User).filter(models.User.id == user_id).first()
    template = (
        db.query(models.Template).filter(models.Template.id == template_id).first()
    )
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()

    if not all([user, template, entity]):
        raise HTTPException(
            status_code=404, detail="User, template, or entity not found."
        )

    # Prepare and send the email
    mail_context = {
        "name": token_data["name"],
        "surname": token_data["surname"],
    }
    mail_content = prepare_mail(template.content, mail_context)

    sender_email = f"{token_data['name']}.{token_data['surname']}@glasnarodeneu.bg"

    # TODO: Move the mailer out of here
    # WARN: The Mailer has not business here; it should have already prepared all the necessary mails while the user is validating
    mailer = Mailer()
    mailer.send(
        sender={
            "email": sender_email,
            "name": f"{token_data['name']} {token_data['surname']}",
        },
        to=[{"email": entity.email, "name": entity.name}],
        subject=template.name,
        text=mail_content,
        reply_to=token_data["mail"],
    )

    # Record the sent mail and update user timestamp
    sent_mail = models.SentMail(
        user_id=user.id, template_id=template.id, entity_id=entity.id
    )
    db.add(sent_mail)
    user.last_sent_at = datetime.now(timezone.utc)
    db.commit()

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
