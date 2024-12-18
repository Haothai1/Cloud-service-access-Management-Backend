from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

plan_permissions = Table(
    'plan_permissions',
    Base.metadata,
    Column('plan_id', Integer, ForeignKey('plans.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    usage_limit = Column(Integer, nullable=False)
    permissions = relationship("Permission", secondary=plan_permissions)
    subscriptions = relationship("UserSubscription", back_populates="plan")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    endpoint = Column(String, nullable=False)
    description = Column(String, nullable=True)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    plan = relationship("Plan", back_populates="subscriptions")

class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    api_endpoint = Column(String, nullable=False)

class ServiceLog(Base):
    __tablename__ = "service_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_subscriptions.user_id"), nullable=False)
    service_name = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(String, nullable=True)
    service_metadata = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PaymentLog(Base):
    __tablename__ = "payment_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_subscriptions.user_id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False)
    stripe_payment_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
