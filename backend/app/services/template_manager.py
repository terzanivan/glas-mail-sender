from typing import List
from app.services.pb_service import pb
from app.api.models import Template, Entity


class TemplateManager:
    @staticmethod
    def get_templates() -> List[Template]:
        records = pb.collection("templates").get_full_list()
        return [Template.model_validate(r) for r in records]

    @staticmethod
    def get_template(template_id: str) -> Template:
        record = pb.collection("templates").get_one(template_id)
        return Template.model_validate(record)

    @staticmethod
    def fill_template(content: str, **replacers: str) -> str:
        for target, value in replacers.items():
            content.replace(target, value)
        return content

    @staticmethod
    def get_associated_entities(template_id: str) -> List[Entity]:
        # Assuming target_entities is a relation field in templates
        template_record = pb.collection("templates").get_one(
            template_id, {"expand": "target_entities"}
        )
        entities = template_record.expand.get("target_entities", [])
        return [Entity.model_validate(e) for e in entities]


template_manager = TemplateManager()
