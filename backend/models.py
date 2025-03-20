from sqlalchemy import Column, Integer, String
from db import Base

class PlayerProgress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    last_checkpoint = Column(String)
