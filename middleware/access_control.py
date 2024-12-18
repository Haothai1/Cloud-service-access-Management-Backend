from functools import wraps
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserSubscription, ServiceLog
import logging

logger = logging.getLogger(__name__)

def check_access(endpoint: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user_id: int, db: Session = Depends(get_db), **kwargs):
            try:
                logger.info(f"Checking access for user {user_id} to endpoint {endpoint}")
                
                # Get user subscription with plan
                subscription = db.query(UserSubscription).filter(
                    UserSubscription.user_id == user_id
                ).first()
                
                if not subscription:
                    logger.warning(f"No subscription found for user {user_id}")
                    raise HTTPException(
                        status_code=404,
                        detail=f"No subscription found for user {user_id}. Please subscribe to a plan first."
                    )
                
                if not subscription.plan:
                    logger.warning(f"No plan found for subscription {subscription.id}")
                    raise HTTPException(
                        status_code=404,
                        detail=f"No plan found for subscription. Please contact support."
                    )

                logger.info(f"User {user_id} has plan: {subscription.plan.name}")
                logger.info(f"Current usage: {subscription.usage_count}/{subscription.plan.usage_limit}")

                # Check usage limits
                if subscription.usage_count >= subscription.plan.usage_limit:
                    logger.warning(f"Usage limit exceeded for user {user_id}")
                    raise HTTPException(
                        status_code=429,
                        detail=f"Usage limit exceeded. Current: {subscription.usage_count}, Limit: {subscription.plan.usage_limit}"
                    )
                
                # Track usage
                subscription.usage_count += 1
                
                # Log service usage
                service_log = ServiceLog(
                    user_id=user_id,
                    service_name=endpoint,
                    endpoint=endpoint,
                    status="success"
                )
                db.add(service_log)
                
                try:
                    db.commit()
                except Exception as commit_error:
                    logger.error(f"Error committing changes: {commit_error}")
                    db.rollback()
                    raise HTTPException(
                        status_code=500,
                        detail="Error updating usage tracking"
                    )
                
                # Execute the endpoint function
                result = await func(user_id=user_id, db=db, *args, **kwargs)
                return result
                
            except HTTPException as he:
                raise he
            except Exception as e:
                logger.error(f"Error in access control: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal server error: {str(e)}"
                )
                
        return wrapper
    return decorator