from email.policy import default

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    number = Column(String(20), nullable=False)
    position = Column(String(50), nullable=False)
    description = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.now())