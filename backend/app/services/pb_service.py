from pocketbase import PocketBase
from app.core.config import settings


def get_pb_client():
    return PocketBase(settings.POCKETBASE_URL)


pb = get_pb_client()
print("user:", settings.POCKETBASE_ADMIN)
pb.collection("_superusers").auth_with_password(
    username_or_email=settings.POCKETBASE_ADMIN,
    password=settings.POCKETBASE_ADMIN_PW,
)
