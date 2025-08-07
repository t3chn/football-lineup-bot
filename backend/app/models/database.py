"""Database models and base class."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

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
    """User management for API access and Telegram integration."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=True, index=True)  # Telegram user ID
    username = Column(String(100), nullable=True, index=True)  # Make nullable for Telegram users
    first_name = Column(String(100), nullable=True)  # Telegram first name
    last_name = Column(String(100), nullable=True)  # Telegram last name
    language_code = Column(String(10), nullable=True)  # User language preference
    email = Column(String(255), unique=True, nullable=True, index=True)
    api_key_hash = Column(String(255), unique=True, nullable=True)  # Hashed API key
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime, nullable=True)
