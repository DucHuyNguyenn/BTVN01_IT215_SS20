from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    # 1-1 relationship with UserProfile
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # 1-1 relationship back to User
    user = relationship("User", back_populates="profile")
