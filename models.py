# models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    phone_number = Column(String)

    def __repr__(self):
        return f"<User(username={self.username}, phone_number={self.phone_number})>"
