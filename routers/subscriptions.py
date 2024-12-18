from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import UserSubscription, UsageLog, Plan
from schemas import SubscriptionCreate, UserSubscriptionResponse
from typing import List

router = APIRouter(
    prefix="",
    tags=["Subscriptions"]
)

@router.post("/subscriptions")
async def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    try:
        # Check if subscription already exists
        existing_sub = db.query(UserSubscription).filter_by(user_id=subscription.user_id).first()
        if existing_sub:
            # If it exists, update it instead
            existing_sub.plan_id = subscription.plan_id
            existing_sub.usage_count = 0  # Reset usage count
            db.commit()
            return {
                "message": "Subscription updated successfully",
                "subscription": {
                    "user_id": existing_sub.user_id,
                    "plan_id": existing_sub.plan_id,
                    "usage_count": existing_sub.usage_count
                }
            }
        
        # If it doesn't exist, create new subscription
        db_sub = UserSubscription(
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            usage_count=0
        )
        db.add(db_sub)
        db.commit()
        db.refresh(db_sub)
        return {
            "message": "Subscription created successfully",
            "subscription": {
                "user_id": db_sub.user_id,
                "plan_id": db_sub.plan_id,
                "usage_count": db_sub.usage_count
            }
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error creating subscription. Please check if plan_id {subscription.plan_id} exists."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/subscriptions/{user_id}")
async def get_subscription(user_id: int, db: Session = Depends(get_db)):
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@router.get("/subscriptions/{user_id}/usage", tags=["Subscriptions"])
@router.get("/{user_id}/usage")  # Add alternative route without 'subscriptions' prefix
async def get_subscription_usage(user_id: int, db: Session = Depends(get_db)):
    # Get subscription
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail=f"Subscription not found for user {user_id}")
    
    # Get plan details
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan not found for subscription")
    
    return {
        "user_id": user_id,
        "plan_name": plan.name,
        "current_usage": subscription.usage_count,
        "usage_limit": plan.usage_limit,
        "remaining_calls": plan.usage_limit - subscription.usage_count
    }

@router.put("/subscriptions/{user_id}")
async def update_subscription(user_id: int, subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    db_sub = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db_sub.plan_id = subscription.plan_id
    db_sub.usage_count = 0  # Reset usage count on plan change
    db.commit()
    return {"message": "Subscription updated successfully"}

@router.get("/users", response_model=List[UserSubscriptionResponse])
async def get_all_users(db: Session = Depends(get_db)):
    try:
        # Get all subscriptions with their associated plans
        subscriptions = db.query(UserSubscription).all()
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserSubscriptionResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="User not found")
    return subscription
