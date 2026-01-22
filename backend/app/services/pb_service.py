from pocketbase import PocketBase
from app.core.config import settings

def get_pb_client():
    return PocketBase(settings.POCKETBASE_URL)

pb = get_pb_client()
