from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, CheckConstraint, Boolean, Date, Time, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.db_postgres import Base



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
    __table__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    email_credential = Column(String, nullable=True)
    email_token = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Income", back_populates="user", cascade="all, delete-orphan")
    setting = relationship("Setting", back_populates="user", cascade="delete-orphan")

class Setting(Base):
    __tablename__ = "setting"

    id = Column(Integer, primary_key=True, index=True)
    auto_label = Column(Integer, default=True)
    auto_response = Column(Boolean, default=False)
    create_draft = Column(Boolean, default=True)
    schedule_event = Column(Boolean, default=False)
    generate_report = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="setting")



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
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

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
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="incomes") 


# Maintain Google Calendar
class Event(Base):
    __table__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    event_title = Column(String, nullable=False)
    related = Column(String, nullable=True) # Related Source/ Pushed From
    usability = Column(Numeric(1, 1), nullable=False)
    calender_set = Column(Boolean, nullable=False, default=0)
    urgency = Column(Boolean, nullable=False, default=False)
    event_date = Column(Date, nullable=True)
    event_time = Column(Time, nullable=True)
    mail_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="events")

