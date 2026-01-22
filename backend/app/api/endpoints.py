from typing import Any
from fastapi import APIRouter, HTTPException, Request
from app.api.models import OTPRequest, VerifyRequest
from app.core.security import hash_email
from app.core.config import settings
from app.services.pb_service import pb
from app.services.authenticator import authenticator
from app.services.mail_service import mail_sender
from app.services.template_manager import template_manager
from datetime import datetime, timedelta, timezone

router = APIRouter()


@router.get("/templates")
async def get_templates():
    return template_manager.get_templates()


@router.get("/templates/{template_id}/preview")
async def preview_template(template_id: str, name: str, surname: str):
    template: Any = template_manager.get_template(template_id)
    content = template_manager.fill_template(template.content, name, surname)
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
        to_email=payload.mail,
        subject="Вашият код за потвърждение",
        content=f"Вашият код за потвърждение е: {code}",
    )

    return {"message": "OTP sent"}


@router.post("/verify-and-send")
async def verify_and_send(payload: VerifyRequest):
    mail_hash = hash_email(payload.mail)

    is_valid = await authenticator.verify_code(mail_hash, payload.otp_code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Get template and entity
    template: Any = template_manager.get_template(payload.template_id)
    entity: Any = pb.collection("entities").get_one(payload.entity_id)

    content = template_manager.fill_template(
        template.content, payload.name, payload.surname
    )
    reply_to = f"{payload.name}.{payload.surname}@{settings.DOMAIN_NAME}"

    # Send actual mail to entity
    await mail_sender.send_mail(
        to_email=entity.email,
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
