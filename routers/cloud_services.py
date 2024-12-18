from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query, Body
from services.clients import (
    stripe, es_client, redis_client, 
    get_auth0_token, get_rabbitmq_channel, get_s3_client
)
from schemas import ServiceLogResponse
from models import ServiceLog
import logging
from middleware.access_control import check_access
from sqlalchemy.orm import Session
from database import get_db
from config import get_settings
from utils.service_logger import log_service_call, log_payment
from typing import List
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(tags=["Cloud Services"])
settings = get_settings()
logger = logging.getLogger(__name__)

# Add request model
class ServiceLogCreate(BaseModel):
    user_id: int
    status: str = "success"

# 1. Stripe Payment Service
@router.get("/cloud-service-1/logs", response_model=List[ServiceLogResponse])
async def get_payment_service_logs(db: Session = Depends(get_db)):
    """Get all payment service usage logs"""
    logs = db.query(ServiceLog).filter(
        ServiceLog.service_name == "cloud-service-1"
    ).all()
    return [
        ServiceLogResponse(
            service_name=log.service_name,
            status=log.status,
            timestamp=log.timestamp
        ) for log in logs
    ]

@router.get("/cloud-service-1")
@check_access("cloud-service-1")
async def get_payment_service(user_id: int, db: Session = Depends(get_db)):
    return {
        "service": "Payment Service",
        "status": "active",
        "description": "Stripe payment processing service"
    }

@router.post("/cloud-service-1/payment")
@check_access("cloud-service-1")
async def create_payment(
    user_id: int,
    db: Session = Depends(get_db)
):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=1000,
            currency="usd"
        )
        await log_payment(
            db=db,
            user_id=user_id,
            amount=10.00,
            currency="usd",
            status="success",
            stripe_payment_id=payment_intent.id
        )
        return {"client_secret": payment_intent.client_secret}
    except Exception as e:
        await log_payment(
            db=db,
            user_id=user_id,
            amount=10.00,
            currency="usd",
            status="failed"
        )
        raise HTTPException(status_code=500, detail=str(e))

# 2. Auth0 Authentication
@router.get("/cloud-service-2/logs", response_model=List[ServiceLogResponse])
async def get_auth_service_logs(db: Session = Depends(get_db)):
    """Get all auth service usage logs"""
    logs = db.query(ServiceLog).filter(
        ServiceLog.service_name == "cloud-service-2"
    ).all()
    return [
        ServiceLogResponse(
            service_name=log.service_name,
            status=log.status,
            timestamp=log.timestamp
        ) for log in logs
    ]

@router.get("/cloud-service-2")
@check_access("cloud-service-2")
async def get_auth_service(user_id: int, db: Session = Depends(get_db)):
    return {
        "service": "Authentication Service",
        "status": "active",
        "description": "Auth0 authentication service"
    }

@router.get("/cloud-service-2/auth")
@check_access("cloud-service-2")
async def get_auth_token(user_id: int, db: Session = Depends(get_db)):
    try:
        token = get_auth0_token()
        return {"access_token": token['access_token']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. AWS S3 Storage
@router.get("/cloud-service-3/logs", response_model=List[ServiceLogResponse])
async def get_storage_service_logs(db: Session = Depends(get_db)):
    """Get all storage service usage logs"""
    logs = db.query(ServiceLog).filter(
        ServiceLog.service_name == "cloud-service-3"
    ).all()
    return [
        ServiceLogResponse(
            service_name=log.service_name,
            status=log.status,
            timestamp=log.timestamp
        ) for log in logs
    ]

@router.get("/cloud-service-3")
@check_access("cloud-service-3")
async def get_storage_service(user_id: int, db: Session = Depends(get_db)):
    return {
        "service": "Storage Service",
        "status": "active",
        "description": "AWS S3 storage service"
    }

@router.post("/cloud-service-3/storage")
@check_access("cloud-service-3")
async def upload_file(
    user_id: int = Query(..., description="User ID is required"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a file to S3"""
    try:
        logger.info(f"Uploading file for user {user_id}: {file.filename}")
        s3_client = get_s3_client()
        
        # Generate a unique filename
        filename = f"user_{user_id}/{file.filename}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file.file,
            settings.AWS_BUCKET_NAME,
            filename
        )
        
        logger.info(f"File uploaded successfully: {filename}")
        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "bucket": settings.AWS_BUCKET_NAME
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

# Add POST endpoint for service 3 logs
@router.post("/cloud-service-3/logs", response_model=ServiceLogResponse)
async def create_storage_service_log(
    user_id: int = Query(..., description="User ID is required"),
    db: Session = Depends(get_db)
):
    """Create a new log entry for storage service"""
    try:
        new_log = ServiceLog(
            user_id=user_id,
            service_name="cloud-service-3",
            endpoint="cloud-service-3/logs",
            status="success",
            timestamp=datetime.utcnow()
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        
        return ServiceLogResponse(
            service_name=new_log.service_name,
            status=new_log.status,
            timestamp=new_log.timestamp
        )
    except Exception as e:
        logger.error(f"Error creating log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 4. Elasticsearch Search
@router.get("/cloud-service-4/logs", response_model=List[ServiceLogResponse])
async def get_search_service_logs(db: Session = Depends(get_db)):
    """Get all search service usage logs"""
    logs = db.query(ServiceLog).filter(
        ServiceLog.service_name == "cloud-service-4"
    ).all()
    return [
        ServiceLogResponse(
            service_name=log.service_name,
            status=log.status,
            timestamp=log.timestamp
        ) for log in logs
    ]

@router.get("/cloud-service-4")
@check_access("cloud-service-4")
async def get_search_service(user_id: int, db: Session = Depends(get_db)):
    return {
        "service": "Search Service",
        "status": "active",
        "description": "Elasticsearch search service"
    }

@router.get("/cloud-service-4/search")
@check_access("cloud-service-4")
async def search_documents(query: str, user_id: int, db: Session = Depends(get_db)):
    try:
        result = es_client.search(
            index="your_index",
            body={
                "query": {
                    "match": {
                        "content": query
                    }
                }
            }
        )
        return {"results": result['hits']['hits']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. RabbitMQ Message Queue
@router.get("/cloud-service-5/logs", response_model=List[ServiceLogResponse])
async def get_queue_service_logs(db: Session = Depends(get_db)):
    """Get all queue service usage logs"""
    logs = db.query(ServiceLog).filter(
        ServiceLog.service_name == "cloud-service-5"
    ).all()
    return [
        ServiceLogResponse(
            service_name=log.service_name,
            status=log.status,
            timestamp=log.timestamp
        ) for log in logs
    ]

@router.get("/cloud-service-5")
@check_access("cloud-service-5")
async def get_queue_service(user_id: int, db: Session = Depends(get_db)):
    return {
        "service": "Message Queue Service",
        "status": "active",
        "description": "RabbitMQ message queue service"
    }

@router.post("/cloud-service-5/queue")
@check_access("cloud-service-5")
async def send_message(message: str, user_id: int, db: Session = Depends(get_db)):
    try:
        channel = get_rabbitmq_channel()
        channel.queue_declare(queue='hello')
        channel.basic_publish(
            exchange='',
            routing_key='hello',
            body=message
        )
        return {"message": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. Redis Cache
@router.get("/cloud-service-6/logs", response_model=List[ServiceLogResponse])
async def get_cache_service_logs(db: Session = Depends(get_db)):
    """Get all cache service usage logs"""
    logs = db.query(ServiceLog).filter(
        ServiceLog.service_name == "cloud-service-6"
    ).all()
    return [
        ServiceLogResponse(
            service_name=log.service_name,
            status=log.status,
            timestamp=log.timestamp
        ) for log in logs
    ]

@router.get("/cloud-service-6")
@check_access("cloud-service-6")
async def get_cache_service(user_id: int, db: Session = Depends(get_db)):
    return {
        "service": "Cache Service",
        "status": "active",
        "description": "Redis cache service"
    }

@router.get("/cloud-service-6/cache/{key}")
@check_access("cloud-service-6")
async def get_cached_data(key: str, user_id: int, db: Session = Depends(get_db)):
    try:
        value = redis_client.get(key)
        if value is None:
            return {"message": "Key not found"}
        return {"key": key, "value": value.decode('utf-8')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cloud-service-6/cache")
@check_access("cloud-service-6")
async def set_cached_data(key: str, value: str, user_id: int, db: Session = Depends(get_db)):
    try:
        redis_client.set(key, value)
        return {"message": "Value cached successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all service logs
@router.get("/services/logs", response_model=List[ServiceLogResponse])
async def get_all_service_logs(db: Session = Depends(get_db)):
    """Get logs for all services"""
    try:
        logs = db.query(ServiceLog).all()
        return [
            ServiceLogResponse(
                service_name=log.service_name,
                status=log.status,
                timestamp=log.timestamp
            ) for log in logs
        ]
    except Exception as e:
        logger.error(f"Error fetching service logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
