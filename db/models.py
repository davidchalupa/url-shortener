from sqlalchemy import Column, Integer, String, Index
from .base import Base

class Shorthand(Base):
    __tablename__ = "shorthands"

    id = Column(Integer, primary_key=True)
    full_url = Column(String, nullable=False)
    short_url_code = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_shorthands_short_url_code", "short_url_code", unique=True),
    )
