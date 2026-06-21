from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .api.v1.endpoints import auth, pets, devices, health, alerts, fitbark, subscriptions, practices, analysis, notifications, users
from .services.ingestion import sync_all_devices
import asyncio

app = FastAPI(title="PawPulse API")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Start the background polling task
    asyncio.create_task(polling_task())

async def polling_task():
    while True:
        try:
            logger.info("Starting background sync for all devices")
            await sync_all_devices()
        except Exception as e:
            logger.error(f"Error in background polling task: {e}")
        
        # Wait for 2 hours
        await asyncio.sleep(7200)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(pets.router, prefix="/api/v1/pets", tags=["pets"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["devices"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(fitbark.router, prefix="/api/v1/fitbark", tags=["fitbark"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
app.include_router(practices.router, prefix="/api/v1/practices", tags=["practices"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to PawPulse API"}
