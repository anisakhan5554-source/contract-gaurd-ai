import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set")
        _engine = create_engine(DATABASE_URL)
    return _engine

def SessionLocal():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()