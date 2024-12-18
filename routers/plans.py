from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Plan
from schemas import PlanCreate, PlanResponse
from typing import List
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Plans"])

@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(db: Session = Depends(get_db)):
    try:
        plans = db.query(Plan).all()
        return plans
    except Exception as e:
        logger.error(f"Error fetching plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plans", response_model=PlanResponse)
async def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    try:
        # Check if plan with same name exists
        existing_plan = db.query(Plan).filter(Plan.name == plan.name).first()
        if existing_plan:
            raise HTTPException(
                status_code=400,
                detail=f"Plan with name '{plan.name}' already exists"
            )
        
        # Create new plan
        db_plan = Plan(
            name=plan.name,
            description=plan.description,
            usage_limit=plan.usage_limit
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
        
    except HTTPException as he:
        raise he
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
def update_plan(plan_id: int, plan: PlanCreate, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db_plan.name = plan.name
    db_plan.description = plan.description
    db_plan.usage_limit = plan.usage_limit
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db.delete(db_plan)
    db.commit()
    return {"message": "Plan deleted successfully"}
