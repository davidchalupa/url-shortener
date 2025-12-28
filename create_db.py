from db.base import Base
from db.session import engine
# this last import ensures that models are registered
from db import models

Base.metadata.create_all(bind=engine)
print("Database created.")
