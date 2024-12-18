# CLOUD SERVICE ACCESS MANAGEMENT BACKEND

## Overview
A FastAPI-based backend service for managing cloud service access and usage tracking.

## Prerequisites
- Python 3.10+
- pip
- Git

## INSTALLATION GUIDE

### Clone Repository
Use `git clone` to get the repository:
```bash
git clone https://github.com/yourusername/cloud-service-access-management.git
cd cloud-service-access-management
```

### Virtual Environment Setup
Create and activate a virtual environment:

#### For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### For macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

#### Option A - Using requirements.txt:
```bash
pip install -r requirements.txt
```

#### Option B - Manual Installation:

##### Core Dependencies:
```bash
pip install fastapi
pip install "uvicorn[standard]"
pip install sqlalchemy
pip install pydantic
pip install python-dotenv
pip install python-multipart
```

##### Cloud Service Dependencies:
```bash
pip install boto3
pip install elasticsearch
pip install redis
pip install pika
pip install stripe
pip install python-jose[cryptography]
pip install auth0-python
```

### Environment Setup
Create a `.env` file in the root directory with these configurations:

#### Core:
```env
DATABASE_URL=sqlite:///./cloud_access.db
```

#### AWS Configuration:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
AWS_BUCKET_NAME=your_bucket_name
```

#### Other Services:
```env
STRIPE_SECRET_KEY=your_stripe_key
AUTH0_DOMAIN=your_domain
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672
```

### Database Initialization
The SQLite database will automatically create on the first run.

## RUNNING THE APPLICATION

### Development Mode:
```bash
uvicorn main:app --reload --log-level debug
```

### Production Mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Documentation Access:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure:
```
/cloud-service-access-management
  main.py
  config.py
  database.py
  models.py
  schemas.py
  requirements.txt
  /routers
  /middleware
  /services
  /static
```

## TROUBLESHOOTING

### Common Issues:

#### 1. Module Not Found Errors
**Solution**: Install the missing module:
```bash
pip install [missing-module]
```

#### 2. Database Connection Issues
- Verify `DATABASE_URL` in `.env`.
- Check SQLite file permissions.

#### 3. Port Already in Use
**Solution**: Use an alternative port:
```bash
uvicorn main:app --port 8001

# TESTING in Postman

## 1. ADMIN ROLE TESTING

### A. Plan Management

#### Create Plan
```http
POST http://localhost:8000/api/plans
```
```json
{
  "name": "Premium Plan",
  "description": "Full Access Plan",
  "permissions": ["storage_access", "payment_access", "search_access"],
  "usage_limit": 1000
}
```

#### Modify Plan
```http
PUT http://localhost:8000/api/plans/1
```
```json
{
  "usage_limit": 2000,
  "permissions": ["all_access"]
}
```

#### Delete Plan
```http
DELETE http://localhost:8000/api/plans/1
```

#### List All Plans
```http
GET http://localhost:8000/api/plans
```

### B. Permission Management

#### Create Permission
```http
POST http://localhost:8000/api/permissions
```
```json
{
  "name": "storage_access",
  "endpoint": "/cloud-service-3/storage",
  "description": "Access to storage API"
}
```

#### Modify Permission
```http
PUT http://localhost:8000/api/permissions/1
```
```json
{
  "description": "Updated storage access permission"
}
```

#### Delete Permission
```http
DELETE http://localhost:8000/api/permissions/1
```

#### List Permissions
```http
GET http://localhost:8000/api/permissions
```

## 2. CUSTOMER ROLE TESTING

### A. Subscription Management

#### View Available Plans
```http
GET http://localhost:8000/api/plans
```

#### Subscribe to Plan
```http
POST http://localhost:8000/api/subscriptions
```
```json
{
  "user_id": 1,
  "plan_id": 1
}
```

#### View Subscription Details
```http
GET http://localhost:8000/api/subscriptions/1
```

#### View Usage Statistics
```http
GET http://localhost:8000/api/subscriptions/1/usage
```

## 3. CLOUD SERVICES TESTING

### A. Service 1 - Payment API

#### Get Payment Info
```http
GET http://localhost:8000/api/cloud-service-1?user_id=1
```

#### Make Payment
```http
POST http://localhost:8000/api/cloud-service-1/payment?user_id=1
```
```json
{
  "amount": 100
}
```

### B. Service 2 - Auth API

#### Authenticate User
```http
GET http://localhost:8000/api/cloud-service-2?user_id=1
```

#### Create Auth Token
```http
POST http://localhost:8000/api/cloud-service-2/auth?user_id=1
```
```json
{
  "username": "test"
}
```

### C. Service 3 - Storage API

#### Get Storage Info
```http
GET http://localhost:8000/api/cloud-service-3?user_id=1
```

#### Upload File
```http
POST http://localhost:8000/api/cloud-service-3/storage?user_id=1
```
[Form-Data: file]

### D. Service 4 - Search API

#### Perform Search
```http
GET http://localhost:8000/api/cloud-service-4?user_id=1
```

#### Search Query
```http
GET http://localhost:8000/api/cloud-service-4/search?user_id=1&query=test
```

### E. Service 5 - Queue API

#### Get Queue Info
```http
GET http://localhost:8000/api/cloud-service-5?user_id=1
```

#### Send Message
```http
POST http://localhost:8000/api/cloud-service-5/message?user_id=1
```
```json
{
  "message": "test"
}
```

### F. Service 6 - Cache API

#### Get Cache Info
```http
GET http://localhost:8000/api/cloud-service-6?user_id=1
```

#### Set Cache Data
```http
POST http://localhost:8000/api/cloud-service-6/cache?user_id=1
```
```json
{
  "key": "test",
  "value": "data"
}
```

## 4. ACCESS CONTROL TESTING

### A. Permission Testing

#### Test Without Permission
```http
GET http://localhost:8000/api/cloud-service-1?user_id=2
```

#### Test With Permission
```http
GET http://localhost:8000/api/cloud-service-1?user_id=1
```

### B. Usage Limit Testing

#### Check Current Usage
```http
GET http://localhost:8000/api/subscriptions/1/usage
```

#### Test Limit Enforcement
Make multiple requests until the limit is reached:
```http
GET http://localhost:8000/api/cloud-service-1?user_id=1
```

## 5. USAGE TRACKING TESTING

### A. Service Logs

#### View All Logs
```http
GET http://localhost:8000/api/services/logs
```

#### View Service-Specific Logs
```http
GET http://localhost:8000/api/cloud-service-1/logs
```

#### View User-Specific Logs
```http
GET http://localhost:8000/api/services/logs?user_id=1
```

### B. Usage Statistics

#### Current Usage
```http
GET http://localhost:8000/api/subscriptions/1/usage
```

#### Usage History
```http
GET http://localhost:8000/api/subscriptions/1/usage/history
```

## VERIFICATION CHECKLIST

### 1. Plan Management
- Plans can be created with permissions
- Plans can be modified
- Plans can be deleted
- Usage limits are enforced

### 2. Permission System
- Permissions are created correctly
- Permissions are enforced
- Permission modifications take effect
- Permission deletion works

### 3. Subscription Management
- Users can subscribe to plans
- Subscription details are accurate
- Usage tracking works
- Plan changes are reflected

### 4. Access Control
- Permission checks work
- Usage limits are enforced
- Temporary restrictions work
- Access is restored after limit reset

### 5. Usage Tracking
- All API calls are logged
- Usage counts are accurate
- Logs show correct timestamps
- User-specific tracking works
