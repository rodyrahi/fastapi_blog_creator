from sqlalchemy import Column, Integer, String
from database import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    filename = Column(String, unique=True)