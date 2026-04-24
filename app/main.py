from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.api import webhook, internal
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.services.reminder_service import start_reminder_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting WhatsApp Booking Assistant...")
    await connect_to_mongo()
    start_reminder_scheduler()
    logger.info("✅ All services started successfully")
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()

app = FastAPI(
    title="WhatsApp Booking Assistant",
    description="AI-powered booking system for local businesses",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, prefix="/webhook", tags=["WhatsApp Webhook"])
app.include_router(internal.router, prefix="/api", tags=["Internal API"])

@app.get("/")
async def root():
    return {
        "message": "WhatsApp Booking Assistant is running! 🚀",
        "status": "active",
        "endpoints": {
            "webhook": "/webhook/whatsapp",
            "verify": "/webhook/verify",
            "api": "/api/bookings"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "booking-assistant"}