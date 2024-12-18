from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import plans_router, permissions_router, subscriptions_router, access_control_router, cloud_services_router, users_router
from database import Base, engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Drop all tables and recreate them
def init_db():
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped all existing tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Created all database tables successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e

# Initialize database
init_db()

app = FastAPI(title="Cloud Service Access Management System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redirect favicon.ico requests to the static file
@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")

# Include routers
app.include_router(plans_router, prefix="/api")
app.include_router(permissions_router, prefix="/api")
app.include_router(subscriptions_router, prefix="/api")
app.include_router(access_control_router, prefix="/api")
app.include_router(cloud_services_router, prefix="/api")
app.include_router(users_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to Cloud Service Access Management System"}