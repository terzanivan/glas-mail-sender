import logging
import httpx
from typing import List, Dict, Any, Optional
from app.api.models import Entity, EntityType
from app.services.pb_service import pb

logger = logging.getLogger(__name__)


class EntityMaintainer:
    """
    EntityMaintainer is responsible for the periodic update of database entries for
    various government entities. It scrapes the parliament.bg site to do so.
    """

    def __init__(self) -> None:
        self.base_url = "https://parliament.bg/api/v1"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def _fetch(self, endpoint: str) -> Optional[Any]:
        """Generic async fetcher with error handling"""
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching {endpoint}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return None

    def _transform_to_entity(
        self, data: Dict[str, Any], ent_type: EntityType
    ) -> Optional[Entity]:
        """
        Translates raw dictionary data into the application's Entity model.
        Override/implement specific mapping logic here.
        """
        try:
            # TODO: Implement mapping logic - to be refined per endpoint
            return Entity(
                name=data.get("name") or data.get("full_name") or "Unknown",
                email=data.get("email") or "no-reply@parliament.bg",
                ent_type=ent_type,
            )
        except Exception as e:
            logger.warning(f"Failed to transform data to Entity: {e}")
            return None

    async def get_mps(self) -> List[Entity]:
        """
        Fetches all MPs from the external API and translates them into Entity objects.
        """
        raw_list = await self._fetch("/coll-list-ns/bg")
        if not raw_list:
            return []

        entities = []
        # In a real scenario, we might iterate over IDs and fetch details
        for item in raw_list:
            entity = self._transform_to_entity(item, EntityType.MP)
            if entity:
                entities.append(entity)

        return entities

    async def get_committees(self) -> List[Entity]:
        """
        Fetches all committees from the external API and translates them into Entity objects.
        """
        raw_list = await self._fetch("/coll-list/bg/3")
        if not raw_list:
            return []

        entities = []
        for item in raw_list:
            entity = self._transform_to_entity(item, EntityType.GOVERNMENT_ENTITY)
            if entity:
                entities.append(entity)

        return entities

    async def sync_entities(self, entities: List[Entity]):
        """
        Synchronizes the provided list of entities with the PocketBase database.
        Performs an upsert based on the email address.
        """
        for entity in entities:
            try:
                # Check if entity already exists by email
                existing = pb.collection("entities").get_list(
                    1, 1, {"filter": f'email = "{entity.email}"'}
                )

                data = entity.model_dump(exclude={"id", "created", "updated"})

                if existing.items:
                    # Update existing record
                    pb.collection("entities").update(existing.items[0].id, data)
                else:
                    # Create new record
                    pb.collection("entities").create(data)
            except Exception as e:
                logger.error(f"Failed to sync entity {entity.email}: {e}")

    async def run_full_sync(self):
        """Orchestrates the full fetching and synchronization process."""
        logger.info("Starting full entity synchronization...")

        mps = await self.get_mps()
        await self.sync_entities(mps)

        committees = await self.get_committees()
        await self.sync_entities(committees)

        logger.info("Full entity synchronization complete.")
        await self.client.aclose()


entity_maintainer = EntityMaintainer()
