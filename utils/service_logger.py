from sqlalchemy.orm import Session
from models import ServiceLog, PaymentLog
import json

async def log_service_call(
    db: Session,
    user_id: int,
    service_name: str,
    endpoint: str,
    status: str,
    error_message: str = None,
    service_metadata: dict = None
):
    log = ServiceLog(
        user_id=user_id,
        service_name=service_name,
        endpoint=endpoint,
        status=status,
        error_message=error_message,
        service_metadata=json.dumps(service_metadata) if service_metadata else None
    )
    db.add(log)
    db.commit()
    return log

async def log_payment(
    db: Session,
    user_id: int,
    amount: float,
    currency: str,
    status: str,
    stripe_payment_id: str = None
):
    log = PaymentLog(
        user_id=user_id,
        amount=amount,
        currency=currency,
        status=status,
        stripe_payment_id=stripe_payment_id
    )
    db.add(log)
    db.commit()
    return log 