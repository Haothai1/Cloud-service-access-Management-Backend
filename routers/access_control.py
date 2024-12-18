from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserSubscription, Plan
from typing import Optional

router = APIRouter(tags=["Access Control"])

@router.get("/access/{user_id}/{api_request}")
async def check_access(
    user_id: int,
    api_request: str,
    db: Session = Depends(get_db)
):
    # Validate user_id
    if not isinstance(user_id, int) or user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID. Must be a positive integer."
        )

    # Get user subscription
    subscription = db.query(UserSubscription).filter_by(user_id=user_id).first()
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"No subscription found for user {user_id}"
        )

    # Get plan details
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=404,
            detail=f"Plan not found for subscription"
        )

    # Check usage limit
    if subscription.usage_count >= plan.usage_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Usage limit exceeded. Current usage: {subscription.usage_count}, Limit: {plan.usage_limit}"
        )
    
    # Increment usage count
    subscription.usage_count += 1
    db.commit()

    return {
        "message": f"Access granted to {api_request}",
        "user_id": user_id,
        "current_usage": subscription.usage_count,
        "usage_limit": plan.usage_limit
    }

# Add a helper endpoint to check usage
@router.get("/access/{user_id}/usage")
async def check_usage(
    user_id: int,
    db: Session = Depends(get_db)
):
    subscription = db.query(UserSubscription).filter_by(user_id=user_id).first()
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"No subscription found for user {user_id}"
        )

    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    return {
        "user_id": user_id,
        "current_usage": subscription.usage_count,
        "usage_limit": plan.usage_limit if plan else None,
        "remaining_calls": (plan.usage_limit - subscription.usage_count) if plan else 0
    }
