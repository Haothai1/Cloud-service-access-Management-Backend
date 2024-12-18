from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Plan, UserSubscription
from schemas import PlanCreate, PlanResponse
from typing import List
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Plans"])

# Debug endpoint to check if plan exists
@router.get("/plans/debug/{plan_id}")
async def debug_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    return {
        "exists": plan is not None,
        "plan_id": plan_id,
        "plan_details": plan.__dict__ if plan else None
    }

@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(db: Session = Depends(get_db)):
    try:
        plans = db.query(Plan).all()
        logger.info(f"Found {len(plans)} plans")
        return plans
    except Exception as e:
        logger.error(f"Error fetching plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plans", response_model=PlanResponse)
async def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    try:
        db_plan = Plan(
            name=plan.name,
            description=plan.description,
            usage_limit=plan.usage_limit
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        logger.info(f"Created new plan with ID: {db_plan.id}")
        return db_plan
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Plan with name '{plan.name}' already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(plan_id: int, plan: PlanCreate, db: Session = Depends(get_db)):
    try:
        # Log the update attempt
        logger.info(f"Attempting to update plan {plan_id}")
        
        # Query the plan and log the result
        db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
        logger.info(f"Plan query result: {db_plan}")
        
        if not db_plan:
            logger.warning(f"Plan {plan_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Plan with id {plan_id} not found"
            )

        # Update the plan fields
        db_plan.name = plan.name
        db_plan.description = plan.description
        db_plan.usage_limit = plan.usage_limit

        try:
            db.commit()
            db.refresh(db_plan)
            logger.info(f"Successfully updated plan {plan_id}")
            return db_plan
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError while updating plan: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Plan with name '{plan.name}' already exists"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int, 
    force: bool = False,
    db: Session = Depends(get_db)
):
    try:
        # Check if plan exists
        db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not db_plan:
            raise HTTPException(
                status_code=404, 
                detail=f"Plan with id {plan_id} not found"
            )

        # Check for existing subscriptions
        existing_subscriptions = db.query(UserSubscription).filter(
            UserSubscription.plan_id == plan_id
        ).all()

        if existing_subscriptions:
            if not force:
                # If force=false, prevent deletion
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot delete plan {plan_id} because it has active subscriptions. Use force=true to delete anyway."
                )
            else:
                # If force=true, delete subscriptions first
                logger.warning(f"Force deleting plan {plan_id} and its subscriptions")
                for subscription in existing_subscriptions:
                    db.delete(subscription)

        # Now delete the plan
        db.delete(db_plan)
        db.commit()
        logger.info(f"Successfully deleted plan {plan_id}")
        
        return {"message": f"Plan {plan_id} deleted successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
