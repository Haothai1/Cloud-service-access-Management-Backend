from sqlalchemy.orm import Session
from models import UserSubscription, UsageLog
from fastapi import HTTPException
from datetime import datetime

# Function to increment usage count
def increment_usage(user_id: int, api_endpoint: str, db: Session):
    """
    Increment the usage count for a user and log the API request.

    Args:
        user_id (int): The ID of the user.
        api_endpoint (str): The endpoint being accessed.
        db (Session): Database session.
    """
    # Fetch user's subscription
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Fetch the plan usage limit
    plan = db.query(UserSubscription).filter(UserSubscription.plan_id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    # Check if usage limit is exceeded
    if subscription.usage_count >= plan.usage_limit:
        raise HTTPException(status_code=403, detail="Usage limit exceeded for this plan")

    # Increment usage and log the API call
    subscription.usage_count += 1
    usage_log = UsageLog(user_id=user_id, api_endpoint=api_endpoint)
    db.add(usage_log)
    db.commit()

# Function to get usage statistics
def get_usage_stats(user_id: int, db: Session):
    """
    Retrieve the usage statistics for a specific user.

    Args:
        user_id (int): The ID of the user.
        db (Session): Database session.

    Returns:
        dict: Usage statistics including usage count and API logs.
    """
    # Fetch subscription
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Fetch usage logs
    usage_logs = db.query(UsageLog).filter(UsageLog.user_id == user_id).all()

    return {
        "user_id": user_id,
        "usage_count": subscription.usage_count,
        "api_calls": [{"api_endpoint": log.api_endpoint, "timestamp": datetime.now()} for log in usage_logs]
    }

@router.get("/usage/{user_id}/limit")
async def check_limit_status(user_id: int, db: Session = Depends(get_db)):
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    remaining_calls = plan.usage_limit - subscription.usage_count
    
    return {
        "user_id": user_id,
        "plan_name": plan.name,
        "usage_count": subscription.usage_count,
        "usage_limit": plan.usage_limit,
        "remaining_calls": remaining_calls,
        "limit_exceeded": subscription.usage_count >= plan.usage_limit
    }

@router.post("/usage/{user_id}")
async def track_api_request(user_id: int, api_endpoint: str, db: Session = Depends(get_db)):
    try:
        increment_usage(user_id, api_endpoint, db)
        return {"message": "API request tracked successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
