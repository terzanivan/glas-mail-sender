import csv
import os
from sqlalchemy.orm import sessionmaker
from app.database import engine, Base
from app.models import Template, Entity

# Create tables
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

def seed_data():
    # Seed Templates
    template_dir = "mails/templates"
    for filename in os.listdir(template_dir):
        if filename.endswith(".txt"):
            name = os.path.splitext(filename)[0].replace("-", " ").title()
            with open(os.path.join(template_dir, filename), "r") as f:
                content = f.read()
            template = Template(name=name, content=content)
            session.add(template)

    # Seed Entities
    entity_dir = "mails/addresses"
    for filename in os.listdir(entity_dir):
        if filename.endswith(".csv"):
            with open(os.path.join(entity_dir, filename), "r") as f:
                reader = csv.reader(f)
                next(reader) # Skip header
                for row in reader:
                    name, email = row
                    entity = Entity(name=name, email=email)
                    session.add(entity)
    
    session.commit()

    # Create associations
    # This is a placeholder. The actual associations need to be defined.
    template1 = session.query(Template).filter(Template.name == "Template Business Organizations Employers").first()
    entity1 = session.query(Entity).filter(Entity.email == "mail@bcci.bg").first()
    if template1 and entity1:
        template1.entities.append(entity1)

    template2 = session.query(Template).filter(Template.name == "Template Council Of Ministers Ministry Of Finance").first()
    entity2 = session.query(Entity).filter(Entity.email == "e-docs@minfin.bg").first()
    if template2 and entity2:
        template2.entities.append(entity2)

    template3 = session.query(Template).filter(Template.name == "Template National Assembly All Parliamentary Groups").first()
    entity3 = session.query(Entity).filter(Entity.email == "parliament@parliament.bg").first()
    if template3 and entity3:
        template3.entities.append(entity3)

    session.commit()

if __name__ == "__main__":
    seed_data()
    print("Database seeded successfully!")
