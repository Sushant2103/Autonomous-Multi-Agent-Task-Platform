import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

def get_engine():
    url=os.getenv("DATABASE_URL", "")
    if not url.startswith(("postgresql+psycopg://", "postgresql://")):
        raise RuntimeError("DATABASE_URL must be a PostgreSQL URL (postgresql+psycopg://...)")
    return create_engine(url,pool_pre_ping=True,pool_size=5,max_overflow=5,future=True)

def get_session_factory(): return sessionmaker(bind=get_engine(),expire_on_commit=False)

def check_postgres():
    with get_engine().connect() as connection: return connection.execute(text("SELECT 1")).scalar_one()==1
