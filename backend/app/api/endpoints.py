from typing import List
from fastapi import APIRouter, HTTPException
from app.api.models import OTPRequest, VerifyRequest, Template, Entity
from app.core.security import hash_email
from app.core.config import settings
from app.services.pb_service import pb
from app.services.authenticator import authenticator
from app.services.mail_service import mail_sender
from app.services.template_manager import template_manager
from datetime import datetime, timedelta, timezone

router = APIRouter()


@router.get("/templates", response_model=List[Template])
async def get_templates():
    return template_manager.get_templates()


@router.get("/templates/{template_id}/preview")
async def preview_template(template_id: str, name: str, surname: str):
    template = template_manager.get_template(template_id)
    ent_id = template.target_entities[0]
    entity_record = pb.collection("entity").get_one(ent_id)
    entity = Entity.model_validate(entity_record)

    replacers = {
        "{user_name}": name,
        "{user_surname}": surname,
        "{entity_name}": entity.name,
    }
    content = template_manager.fill_template(template.content, **replacers)
    return {"content": content}


@router.post("/request-otp")
async def request_otp(payload: OTPRequest):
    mail_hash = hash_email(payload.mail)

    # Check rate limit (168 hours)
    limit_time = datetime.now(timezone.utc) - timedelta(hours=settings.RATE_LIMIT_HOURS)
    existing_logs = pb.collection("sent_logs").get_list(
        1,
        1,
        {
            "filter": f'mail_hash = "{mail_hash}" && created > "{limit_time.isoformat()}"'
        },
    )

    if existing_logs.items:
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Try again later."
        )

    # Check deduplication
    duplicate_template = pb.collection("sent_logs").get_list(
        1,
        1,
        {
            "filter": f'mail_hash = "{mail_hash}" && template_id = "{payload.template_id}"'
        },
    )
    if duplicate_template.items:
        raise HTTPException(
            status_code=400, detail="You have already sent this template."
        )

    # Create OTP session
    _, code = await authenticator.create_auth_session(mail_hash)

    # Send OTP mail
    await mail_sender.send_mail(
        to_email=[payload.mail],
        subject="Вашият код за потвърждение",
        content=f"Вашият код за потвърждение е: {code}",
        sender=f"noreply@{settings.DOMAIN_NAME}",
    )

    return {"message": "OTP sent"}


@router.post("/verify-and-send")
async def verify_and_send(payload: VerifyRequest):
    mail_hash = hash_email(payload.mail)

    is_valid = await authenticator.verify_code(mail_hash, payload.otp_code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # WARN: This assumes that there is only one entity a template can be sent to.
    # There are multiple and the application should do only 1 send action
    template = template_manager.get_template(payload.template_id)
    entity_record = pb.collection("entities").get_one(payload.entity_id)
    entity = Entity.model_validate(entity_record)

    # TODO: The data for the replacement also comes from the entity

    replacers = {
        "{sender_name}": payload.name,
        "{sender_surname}": payload.surname,
        "{sender_domain}": payload.mail.split("@")[1],
        "{entity_name}": entity.name,
    }

    content = template_manager.fill_template(template.content, **replacers)

    reply_to = payload.mail
    sender = f"{replacers['{sender_name}']}.{replacers['{sender_surname}']}@{settings.DOMAIN_NAME}"

    # Send actual mail to entity
    await mail_sender.send_mail(
        to_email=[entity.email],
        sender=sender,
        subject="Гражданско писмо",  # Could be more dynamic
        content=content,
        reply_to=reply_to,
    )

    # Log the send
    pb.collection("sent_logs").create(
        {
            "mail_hash": mail_hash,
            "template_id": payload.template_id,
            "entity_id": payload.entity_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    return {"message": "Mail sent successfully"}
