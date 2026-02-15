# DB Connection Logic

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
from dotenv import load_dotenv

# can move secret vars in .env file and load them here, so they aren't hardcoded in the codebase
load_dotenv()

# should match docker-compose.yml config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_interviewer") 

# Sets up connection infrastructure to DB
engine = create_engine(DATABASE_URL)

# How to interact with the DB. Requests should create a session and then close it. (Temp convo with the database)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Each model/table will inherit from this base class so SQLAlchemy can keep track of them and create the tables in the DB
Base = declarative_base()

# FastAPI dependency injection to allow us to create DB session per request and close it after automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()