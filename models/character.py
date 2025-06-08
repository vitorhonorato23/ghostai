from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    personality = Column(Text, nullable=False)
    style = Column(Text, nullable=False)
    context = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="characters")