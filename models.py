from sqlalchemy import Column, Integer, String, Float, Text
from db import Base

class Spot(Base):
    __tablename__ = "spots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    city = Column(String)
    category = Column(String)
    rating = Column(Float)
    description = Column(Text)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
