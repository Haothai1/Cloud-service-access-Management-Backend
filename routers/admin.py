from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import ServiceLog, PaymentLog
from typing import List
from schemas import ServiceLogResponse, PaymentLogResponse

router = APIRouter(tags=["Admin"])

@router.get("/admin/logs/services/{user_id}", response_model=List[ServiceLogResponse])
async def get_service_logs(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(ServiceLog).filter(ServiceLog.user_id == user_id).all()
    return logs

@router.get("/admin/logs/payments/{user_id}", response_model=List[PaymentLogResponse])
async def get_payment_logs(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(PaymentLog).filter(PaymentLog.user_id == user_id).all()
    return logs 