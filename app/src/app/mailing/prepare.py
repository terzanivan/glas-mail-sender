from string import Template

def prepare_mail(template_content: str, context: dict) -> str:
    """
    Fills a template string with the given context.
    """
    template = Template(template_content)
    return template.substitute(context)
