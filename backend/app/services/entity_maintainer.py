import asyncio
from itertools import zip_longest
import logging
import httpx
from typing import List, Any, Mapping, Optional, TypedDict

from pydantic import BaseModel, Field, HttpUrl, EmailStr

from app.api.models import Entity, EntityType

from app.services.pb_service import pb

logger = logging.getLogger(__name__)


class _p_Mp_Def(BaseModel):
    A_ns_MP_id: int
    A_ns_MPL_Name1: str
    A_ns_MPL_Name2: str
    A_ns_MPL_Name3: str
    A_ns_MP_Email: Optional[EmailStr] = Field(default="invalid@invalid.org")


class _p_Com_Def(BaseModel):
    A_ns_C_id: int
    A_ns_CL_value: str
    A_ns_CDemail: Optional[EmailStr] = Field(default="invalid@invalid.org")


class _entMapping(TypedDict):
    name: str
    email: EmailStr
    url: str


class EntityMaintainer:
    """
    EntityMaintainer is responsible for the periodic update of database entries for
    various government entities. It scrapes the parliament.bg site to do so.
    """

    def __init__(self) -> None:
        # INFO: So, the httpx library sets a User-Agent that triggers the parliament.bg defences. So we replace it.
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        self.base_url = "https://parliament.bg/api/v1"
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=30.0, verify=False, headers=headers
        )

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
        self, data: _entMapping, ent_type: EntityType
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
                ent_source=data.get("url") or "invalid",  # # pyright: ignore[]
            )
        except Exception as e:
            logger.warning(f"Failed to transform data to Entity: {e}")
            return None

    async def get_mps(self) -> List[Entity]:
        async def _process_mp(item) -> Entity | None:
            mp = _p_Mp_Def(**item)
            ent_url = HttpUrl(url=self.base_url + f"/mp-profile/bg/{mp.A_ns_MP_id}")
            resp = await self._fetch(ent_url.encoded_string())
            if not resp:
                logger.warning(
                    f"could not get detail for {EntityType.MP} {mp.A_ns_MP_id}"
                )
                return
            mp.A_ns_MP_Email = resp["A_ns_MP_Email"]
            mp_mapping = _entMapping(
                name=f"{mp.A_ns_MPL_Name1} {mp.A_ns_MPL_Name2} {mp.A_ns_MPL_Name3}",
                email=str(mp.A_ns_MP_Email),
                url=ent_url.__str__(),
            )
            entity = self._transform_to_entity(mp_mapping, EntityType.MP)
            return entity

        """
        Fetches all MPs from the external API and translates them into Entity objects.
        """
        data = await self._fetch("coll-list-ns/bg")
        if not data:
            return []
        raw_entities: List[Mapping] = data["colListMP"]
        entities: List[Entity] = []

        batch_size = 5
        for i in range(0, len(raw_entities), 5):
            batch = raw_entities[i : i + batch_size]
            tasks = [_process_mp(item) for item in batch]
            results = await asyncio.gather(*tasks)
            entities.extend([ent for ent in results if ent is not None])
            if i + batch_size < len(raw_entities):
                logger.info(f"processed {i}/{len(raw_entities)}")
                await asyncio.sleep(1.0)
        return entities

    async def get_committees(self) -> List[Entity]:
        """
        Fetches all committees from the external API and translates them into Entity objects.
        """

        async def _process_committee(item) -> Entity | None:
            comm = _p_Com_Def(**item)
            ent_url = HttpUrl(
                url=self.base_url + f"/coll-list-mp/bg/{comm.A_ns_C_id}/3"
            )
            resp = await self._fetch(ent_url.encoded_string())
            if not resp:
                print(
                    f"could not get detail for {str(EntityType.COMMITTEE)} {comm.A_ns_C_id}"
                )
                return
            comm.A_ns_CDemail = resp["A_ns_CDemail"]
            mp_mapping = _entMapping(
                name=comm.A_ns_CL_value,
                email=str(comm.A_ns_CDemail),
                url=ent_url.__str__(),
            )
            entity = self._transform_to_entity(mp_mapping, EntityType.COMMITTEE)
            return entity

        data = await self._fetch("coll-list/bg/3")
        if not data:
            return []
        raw_entities: List[Mapping] = data
        entities: List[Entity] = []

        batch_size = 5
        for i in range(0, len(raw_entities), 5):
            batch = raw_entities[i : i + batch_size]
            tasks = [_process_committee(item) for item in batch]
            results = await asyncio.gather(*tasks)
            entities.extend([ent for ent in results if ent is not None])
            if i + batch_size < len(raw_entities):
                print(f"processed {i}/{len(raw_entities)})")
                await asyncio.sleep(1.0)
        return entities

    async def sync_entities(self, entities: List[Entity]):
        """
        Synchronizes the provided list of entities with the PocketBase database.
        Performs an upsert based on the email address.
        """
        coll_entity = pb.collection("entity")
        # Prepare the database entities for comparisson
        db_entities_raw = coll_entity.get_full_list(batch=300)
        db_entities_models = [Entity.model_validate(e) for e in db_entities_raw]
        db_entities_map = {
            e.email: e.id for e in db_entities_models if e.id is not None
        }
        db_entities_cmp = set(db_entities_map.keys())

        incoming_entities_cmp = {e.email for e in entities}

        stale_mails = db_entities_cmp - incoming_entities_cmp

        for mail in stale_mails:
            coll_entity.delete(db_entities_map[mail])

        for entity in entities:
            try:
                if entity.email in db_entities_cmp:
                    coll_entity.update(
                        id=db_entities_map[entity.email],
                        body_params=entity.model_dump(
                            exclude={"id", "created", "updated"}
                        ),
                    )
                else:
                    # Create new record
                    coll_entity.create(
                        entity.model_dump(exclude={"id", "created", "updated"})
                    )
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
