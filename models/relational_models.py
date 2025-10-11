from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, CheckConstraint, Boolean, Date, Time, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.relational_db import Base
from datetime import datetime, timedelta

# Base = declarative_base()

"""
Class Format:
    id: int
    type: str
    name: str
    .
    .
    .
    mail_id: str
    user_id: int
    created_at: DateTime
    updated_at: DateTime

    Relationships: All relationship

"""



class User(Base):
    __tablename__ = "user_table"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    fname = Column(String(50), nullable=True)
    lname = Column(String(50), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255),nullable=True)
    google_login = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    setting = relationship("Setting", back_populates="user", cascade="all, delete-orphan")
    user_secret = relationship("UserSecret", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key= True, index=True)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    revoked = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="refresh_tokens", uselist=False)


class UserSecret(Base):
    __tablename__ = "user_secret"

    id = Column(Integer, primary_key=True, index=True)
    client_secret = Column(String, nullable=True)
    client_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_secret", uselist=False)


class Setting(Base):
    __tablename__ = "setting"

    id = Column(Integer, primary_key=True, index=True)
    auto_label = Column(Integer, default=True)
    auto_response = Column(Boolean, default=False)
    create_draft = Column(Boolean, default=True)
    schedule_event = Column(Boolean, default=False)
    generate_report = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="setting", uselist=False)



class Expense(Base):
    __tablename__ = "expense"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False, default="item")  # type -> select[item, service]
    name = Column(String, nullable=False)
    qty = Column(Numeric(5, 2), nullable=True, default=1)
    price = Column(Numeric(5, 2),nullable=False)
    gst = Column(Numeric(2, 2), nullable=True, default=0)
    gst_category = Column(Integer, nullable=True)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    mail_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="expenses")



class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False, default="item")  # type -> select[item, service]
    name = Column(String, nullable=False)
    qty = Column(Numeric(5, 2), nullable=True, default=1)
    price = Column(Numeric(5, 2),nullable=False)
    gst = Column(Numeric(2, 2), nullable=True, default=0)
    gst_category = Column(Integer, nullable=True)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    mail_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="incomes")


# Maintain Google Calendar
class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    event_title = Column(String, nullable=False)
    related = Column(String, nullable=True) # Related Source/ Pushed From
    usability = Column(Numeric(1, 1), nullable=False)
    calender_set = Column(Boolean, nullable=False, default=0)
    urgency = Column(Boolean, nullable=False, default=False)
    event_date = Column(Date, nullable=True)
    event_time = Column(Time, nullable=True)
    mail_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="events")

