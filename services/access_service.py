from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserSubscription, Plan

router = APIRouter(tags=["Access Control"])

def verify_usage_limit(user_id: int, db: Session = Depends(get_db)):
    subscription = db.query(UserSubscription).filter_by(user_id=user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if subscription.usage_count >= plan.usage_limit:
        raise HTTPException(status_code=403, detail="Usage limit exceeded")
    
    subscription.usage_count += 1
    db.commit()
    return subscription

@router.get("/access/{user_id}/{api_request}")
def check_access(
    user_id: int, 
    api_request: str, 
    subscription: UserSubscription = Depends(verify_usage_limit)
):
    return {"message": f"Access granted to {api_request}"}
