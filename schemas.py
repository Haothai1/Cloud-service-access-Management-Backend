from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class PlanBase(BaseModel):
    name: str
    description: str
    usage_limit: int

class PlanCreate(PlanBase):
    permissions: List[int] = []

class PlanResponse(PlanBase):
    id: int
    
    class Config:
        from_attributes = True

class PermissionCreate(BaseModel):
    name: str
    endpoint: str
    description: Optional[str] = None

class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int

class UsageResponse(BaseModel):
    user_id: int
    usage_count: int

class ServiceLogCreate(BaseModel):
    user_id: int
    service_name: str
    endpoint: str
    status: str
    error_message: Optional[str] = None
    service_metadata: Optional[Dict] = None

class ServiceLogResponse(BaseModel):
    service_name: str
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True

class PaymentLogCreate(BaseModel):
    user_id: int
    amount: float
    currency: str
    status: str
    stripe_payment_id: Optional[str] = None

class PaymentLogResponse(PaymentLogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class UserSubscriptionResponse(BaseModel):
    user_id: int
    plan_id: int
    usage_count: int
    created_at: datetime
    plan: Optional[PlanBase] = None

    class Config:
        from_attributes = True
