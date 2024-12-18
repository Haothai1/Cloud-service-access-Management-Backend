from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserSubscription, Plan, ServiceLog
from schemas import SubscriptionCreate, UserSubscriptionResponse, SubscriptionUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("", response_model=UserSubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    try:
        # Check if plan exists
        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Plan with id {subscription.plan_id} not found"
            )

        # Check if user already has an active subscription
        existing_subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == subscription.user_id,
            UserSubscription.is_active == True
        ).first()

        if existing_subscription:
            raise HTTPException(
                status_code=400,
                detail="User already has an active subscription"
            )

        # Create new subscription
        db_subscription = UserSubscription(
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            start_date=datetime.utcnow(),
            is_active=True,
            usage_count=0
        )

        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        logger.info(f"Created subscription for user {subscription.user_id} with plan {subscription.plan_id}")
        
        return db_subscription

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserSubscriptionResponse)
async def get_subscription(user_id: int, db: Session = Depends(get_db)):
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active == True
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )
    
    return subscription

@router.get("/debug/all")
async def list_all_subscriptions(db: Session = Depends(get_db)):
    """Debug endpoint to list all subscriptions"""
    subscriptions = db.query(UserSubscription).all()
    return [{
        "id": sub.id,
        "user_id": sub.user_id,
        "plan_id": sub.plan_id,
        "is_active": sub.is_active,
        "usage_count": sub.usage_count,
        "start_date": sub.start_date,
        "end_date": sub.end_date
    } for sub in subscriptions]

@router.put("/{subscription_id}", response_model=UserSubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    try:
        # Check if subscription exists
        db_subscription = db.query(UserSubscription).filter(
            UserSubscription.id == subscription_id
        ).first()
        
        if not db_subscription:
            raise HTTPException(
                status_code=404,
                detail=f"Subscription with id {subscription_id} not found"
            )

        # If plan_id is being updated, verify the new plan exists
        if subscription.plan_id:
            plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
            if not plan:
                raise HTTPException(
                    status_code=404,
                    detail=f"Plan with id {subscription.plan_id} not found"
                )
            db_subscription.plan_id = subscription.plan_id

        # Update other fields if provided
        if subscription.is_active is not None:
            db_subscription.is_active = subscription.is_active
            if not subscription.is_active:
                db_subscription.end_date = datetime.utcnow()

        if subscription.usage_count is not None:
            db_subscription.usage_count = subscription.usage_count

        db.commit()
        db.refresh(db_subscription)
        logger.info(f"Updated subscription {subscription_id}")
        
        return db_subscription

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/usage")
async def get_subscription_usage(user_id: int, db: Session = Depends(get_db)):
    try:
        # Get active subscription
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="No active subscription found"
            )

        # Get plan details
        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        
        # Get service usage logs
        service_logs = db.query(ServiceLog).filter(
            ServiceLog.user_id == user_id
        ).all()

        return {
            "subscription_id": subscription.id,
            "plan_name": plan.name,
            "usage_count": subscription.usage_count,
            "usage_limit": plan.usage_limit,
            "remaining_calls": plan.usage_limit - subscription.usage_count,
            "is_limit_exceeded": subscription.usage_count >= plan.usage_limit,
            "recent_calls": [
                {
                    "service": log.service_name,
                    "endpoint": log.endpoint,
                    "status": log.status,
                    "timestamp": log.timestamp
                } for log in service_logs[-5:]  # Last 5 calls
            ]
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting subscription usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    force: bool = False,
    db: Session = Depends(get_db)
):
    try:
        # Check if subscription exists
        subscription = db.query(UserSubscription).filter(
            UserSubscription.id == subscription_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=404,
                detail=f"Subscription with id {subscription_id} not found"
            )

        # Check for active service logs
        service_logs = db.query(ServiceLog).filter(
            ServiceLog.user_id == subscription.user_id
        ).all()

        if service_logs and not force:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete subscription {subscription_id} because it has service logs. Use force=true to delete anyway."
            )

        if force:
            # Delete associated service logs
            for log in service_logs:
                db.delete(log)
            logger.warning(f"Force deleting subscription {subscription_id} and its {len(service_logs)} service logs")

        # Delete the subscription
        db.delete(subscription)
        db.commit()
        logger.info(f"Successfully deleted subscription {subscription_id}")
        
        return {"message": f"Subscription {subscription_id} deleted successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting subscription {subscription_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
