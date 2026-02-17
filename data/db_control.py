import os
import json
from datetime import datetime, timedelta
from typing import List, Any, Dict, Optional
import logging

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, func, extract, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from data.models import Base, Client

logger = logging.getLogger('main_logger')

engine = create_engine("sqlite:///data/kilovatt_market.db", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

def add_client(telegram_id: int, name: str, number: str, position: str, description: str) -> Optional[Client]:
    with SessionLocal() as session:
        new_client = Client(
            telegram_id = telegram_id,
            name = name,
            number = number,
            position = position,
            description = description
        )
        session.add(new_client)
        session.commit()
        session.refresh(new_client)
        return new_client

def is_client(client_id: str) -> Optional[Client]:
    with SessionLocal() as session:
        client = session.query(Client).filter(Client.telegram_id == client_id).one_or_none()
        return client