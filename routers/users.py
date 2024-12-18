from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserSubscription, Plan, ServiceLog
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("")
async def get_users(db: Session = Depends(get_db)):
    """Get all users with their subscription status"""
    try:
        # Get unique users from subscriptions
        users = db.query(UserSubscription.user_id).distinct().all()
        user_list = []
        
        for (user_id,) in users:
            # Get active subscription for user
            active_subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.is_active == True
            ).first()
            
            # Get plan details if subscription exists
            plan_details = None
            if active_subscription:
                plan = db.query(Plan).filter(Plan.id == active_subscription.plan_id).first()
                plan_details = {
                    "plan_id": plan.id,
                    "plan_name": plan.name,
                    "usage_count": active_subscription.usage_count,
                    "usage_limit": plan.usage_limit
                }
            
            # Get recent service logs
            recent_logs = db.query(ServiceLog).filter(
                ServiceLog.user_id == user_id
            ).order_by(ServiceLog.timestamp.desc()).limit(5).all()
            
            user_list.append({
                "user_id": user_id,
                "has_active_subscription": active_subscription is not None,
                "subscription_details": plan_details,
                "recent_activity": [
                    {
                        "service": log.service_name,
                        "endpoint": log.endpoint,
                        "status": log.status,
                        "timestamp": log.timestamp
                    } for log in recent_logs
                ]
            })
        
        return user_list

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get details for a specific user"""
    try:
        # Get active subscription
        active_subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True
        ).first()
        
        if not active_subscription:
            return {
                "user_id": user_id,
                "has_active_subscription": False,
                "subscription_details": None,
                "recent_activity": []
            }
        
        # Get plan details
        plan = db.query(Plan).filter(Plan.id == active_subscription.plan_id).first()
        
        # Get recent service logs
        recent_logs = db.query(ServiceLog).filter(
            ServiceLog.user_id == user_id
        ).order_by(ServiceLog.timestamp.desc()).limit(5).all()
        
        return {
            "user_id": user_id,
            "has_active_subscription": True,
            "subscription_details": {
                "plan_id": plan.id,
                "plan_name": plan.name,
                "usage_count": active_subscription.usage_count,
                "usage_limit": plan.usage_limit
            },
            "recent_activity": [
                {
                    "service": log.service_name,
                    "endpoint": log.endpoint,
                    "status": log.status,
                    "timestamp": log.timestamp
                } for log in recent_logs
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 