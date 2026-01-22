from app.services.pb_service import pb

class TemplateManager:
    @staticmethod
    def get_templates():
        return pb.collection("templates").get_full_list()

    @staticmethod
    def get_template(template_id: str):
        return pb.collection("templates").get_one(template_id)

    @staticmethod
    def fill_template(content: str, name: str, surname: str):
        return content.replace("{name}", name).replace("{surname}", surname)

    @staticmethod
    def get_associated_entities(template_id: str):
        # Assuming target_entities is a relation field in templates
        template = pb.collection("templates").get_one(template_id, {"expand": "target_entities"})
        return template.expand.get("target_entities", [])

template_manager = TemplateManager()
