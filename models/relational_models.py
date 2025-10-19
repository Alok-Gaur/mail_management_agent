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
    google_login = Column(Boolean, default=False) # True if user initially signed up using Google OAuth
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=False) # if active == flase, user is suspended from the platform

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    setting = relationship("Setting", back_populates="user", cascade="all, delete-orphan")
    user_secret = relationship("UserSecret", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="user", cascade="all, delete-orphan")
    user_label = relationship("UserLabels", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "fname": self.fname,
            "lname": self.lname,
            "email": self.email,
            "google_login": self.google_login,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active": self.active
        }


class RefreshToken(Base):
    """ Store the system generated refresh tokens """
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key= True, index=True)
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    revoked = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="refresh_tokens", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "token": self.token,
            "expires_at": self.expires_at,
            "revoked": self.revoked,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class UserSecret(Base):
    """ Store users gmail secrets """
    __tablename__ = "user_secret"

    id = Column(Integer, primary_key=True, index=True)
    # Store and manage Google OAuth Tokens
    client_secret = Column(String, nullable=True)
    client_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    revoked = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_secret", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "client_secret": self.client_secret,
            "client_token": self.client_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "revoked": self.revoked,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Setting(Base):
    """ Store basic setting pereferences """
    __tablename__ = "setting"

    id = Column(Integer, primary_key=True, index=True)
    auto_label = Column(Boolean, default=True)
    auto_response = Column(Boolean, default=False)
    create_draft = Column(Boolean, default=True)
    schedule_event = Column(Boolean, default=False)
    generate_report = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="setting", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "auto_label": self.auto_label,
            "auto_response": self.auto_response,
            "create_draft": self.create_draft,
            "schedule_event": self.schedule_event,
            "generate_report": self.generate_report,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class WatchHistory(Base):
    __tablename__ = 'watch_history'

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(String, nullable=False)
    added_by = Column(String, nullable=False)               # eg, hook or watch

    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="watch_history", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "history_id": self.history_id,
            "added_by": self.added_by,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class UserLabels(Base):
    __tablename__ = "user_label"
    id = Column(Integer, primary_key=True, index=True)
    label_name = Column(String, nullable=False, unique=False)
    label_description = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_label", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "label_name": self.label_name,
            "label_description": self.label_description,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "qty": self.qty,
            "price": self.price,
            "gst": self.gst,
            "gst_category": self.gst_category,
            "total": self.total,
            "mail_id": self.mail_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }



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

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "qty": self.qty,
            "price": self.price,
            "gst": self.gst,
            "gst_category": self.gst_category,
            "total": self.total,
            "mail_id": self.mail_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


# Maintain Google Calendar
class Event(Base):
    """ User event scheduled on the calender """
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

    def to_dict(self):
        return {
            "id": self.id,
            "event_title": self.event_title,
            "related": self.related,
            "usability": self.usability,
            "calender_set": self.calender_set,
            "urgency": self.urgency,
            "event_date": self.event_date,
            "event_time": self.event_time,
            "mail_id": self.mail_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

