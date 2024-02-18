from app import app, db
from database_models import Base

with app.app_context():
    Base.metadata.create_all(db.engine)
