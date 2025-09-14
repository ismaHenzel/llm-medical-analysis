import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_user = os.environ.get('POSTGRES_USER', 'postgres')
db_password = os.environ.get('POSTGRES_PASSWORD', 'changeme')
db_host = os.environ.get('DB_HOST', 'postgres')
db_port = os.environ.get('DB_PORT', '5432')
db_name = 'medical_analysis'

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    This is the dependency that will be injected into your path operation functions.
    It creates a new SQLAlchemy SessionLocal for each request, yields it to the
    path operation, and then ensures it's closed when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
