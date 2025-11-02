from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

def get_database_engine():
    """Get database engine with fallback to SQLite"""
    try:
        POSTGRES_URL = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOSTNAME}:{settings.DATABASE_PORT}/{settings.POSTGRES_DB}"
        )
        
        # Test connection
        test_engine = create_engine(POSTGRES_URL)
        test_engine.connect().close()
        
        print("Using PostgreSQL database")
        return create_engine(POSTGRES_URL, echo=True)
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        print("Falling back to SQLite")
        
        # Use SQLite for local development/testing
        SQLITE_URL = "sqlite:///./pizza_api.db"
        return create_engine(SQLITE_URL, echo=True, connect_args={"check_same_thread": False})

engine = get_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_database():
    """Initialize database tables"""
    try:
        from . import models
        models.Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # For SQLite fallback, create tables anyway
        try:
            from . import models
            models.Base.metadata.create_all(bind=engine)
            print("Database tables created with fallback")
        except Exception as fallback_error:
            print(f"Fallback table creation also failed: {fallback_error}")

