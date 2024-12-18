from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import Permission
from schemas import PermissionCreate

router = APIRouter(
    prefix="",
    tags=["Permissions"]
)

@router.post("/permissions")
async def create_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    existing_permission = db.query(Permission).filter(Permission.name == permission.name).first()
    if existing_permission:
        raise HTTPException(
            status_code=400,
            detail=f"Permission with name '{permission.name}' already exists"
        )
    
    try:
        db_permission = Permission(**permission.dict())
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        return {
            "message": "Permission created successfully",
            "permission_id": db_permission.id,
            "permission": db_permission
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not create permission. Please check if it already exists."
        )

@router.get("/permissions")
async def get_permissions(db: Session = Depends(get_db)):
    permissions = db.query(Permission).all()
    return permissions

@router.get("/permissions/{permission_id}")
async def get_permission(permission_id: int, db: Session = Depends(get_db)):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail=f"Permission with id {permission_id} not found")
    return permission

@router.put("/permissions/{permission_id}", tags=["Permissions"])
@router.put("/{permission_id}")
async def update_permission(permission_id: int, permission: PermissionCreate, db: Session = Depends(get_db)):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail=f"Permission with id {permission_id} not found")
    
    try:
        for key, value in permission.dict().items():
            setattr(db_permission, key, value)
        db.commit()
        db.refresh(db_permission)
        return {
            "message": "Permission updated successfully",
            "permission": db_permission
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Permission with name '{permission.name}' already exists"
        )

@router.delete("/permissions/{permission_id}", tags=["Permissions"])
@router.delete("/{permission_id}")
async def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail=f"Permission with id {permission_id} not found")
    
    try:
        db.delete(db_permission)
        db.commit()
        return {"message": f"Permission {permission_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
