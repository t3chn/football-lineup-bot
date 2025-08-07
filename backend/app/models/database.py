"""Database models and base class."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PredictionHistory(Base):
    """Store prediction history for analytics and caching."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String(100), nullable=False, index=True)
    formation = Column(String(20))
    lineup = Column(JSON)  # Store player data as JSON
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(String(100), index=True)  # User ID or API key identifier


class User(Base):
    """User management for API access."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    api_key_hash = Column(String(255), unique=True, nullable=True)  # Hashed API key
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime, nullable=True)
