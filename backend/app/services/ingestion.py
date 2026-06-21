import httpx
import uuid
from datetime import datetime, timedelta
import logging

from ..db.base import query_db, escape_string
from .normalization import normalize_data
from .anomaly import run_anomaly_detection_for_pet
from ..core.config import settings

logger = logging.getLogger(__name__)

FITBARK_BASE_URL = "https://app.fitbark.com/api/v2"
FITBARK_TOKEN_URL = "https://app.fitbark.com/oauth/token"

async def refresh_fitbark_token(device: dict):
    """
    Refresh the FitBark access token using the refresh token.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                FITBARK_TOKEN_URL,
                data={
                    "client_id": settings.FITBARK_CLIENT_ID,
                    "client_secret": settings.FITBARK_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": device["refresh_token"],
                },
            )
            response.raise_for_status()
            token_data = response.json()
            
            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token") or device["refresh_token"]
            expires_in = token_data.get("expires_in", 3600)
            
            expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
            
            query_db(f"UPDATE devices SET access_token = '{access_token}', refresh_token = '{refresh_token}', token_expires_at = '{expires_at}' WHERE id = '{device['id']}'")
            
            # Update the local dict for immediate use
            device["access_token"] = access_token
            device["refresh_token"] = refresh_token
            device["token_expires_at"] = expires_at
            
            return device
        except Exception as e:
            logger.error(f"Failed to refresh FitBark token for device {device['id']}: {e}")
            return None

async def fetch_fitbark_data(external_id: str, access_token: str, start_date: str, end_date: str):
    """
    Fetch hourly activity data from FitBark.
    start_date and end_date in YYYY-MM-DD format.
    """
    headers = {"Authorization": f"Token token={access_token}"}
    payload = {
        "activity_series": {
            "slug": external_id,
            "from": start_date,
            "to": end_date,
            "resolution": "HOURLY"
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{FITBARK_BASE_URL}/activity_series", json=payload, headers=headers)
            if response.status_code == 401:
                # Handle expired token (will be caught by the caller)
                return "UNAUTHORIZED"
            response.raise_for_status()
            data = response.json()
            return data.get("activity_series", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"FitBark API error: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error fetching FitBark data: {e}")
            return []

async def sync_fitbark_device(device: dict, days_back: int = 2):
    """
    Sync data for a single FitBark device.
    days_back: how many days of history to fetch.
    """
    # Check if token is expired (with 5 min buffer)
    if device.get("token_expires_at"):
        expires_at = datetime.fromisoformat(device["token_expires_at"])
        if datetime.utcnow() > (expires_at - timedelta(minutes=5)):
            device = await refresh_fitbark_token(device)
            if not device:
                return

    pet_id = device["pet_id"]
    external_id = device["external_id"]
    access_token = device["access_token"]
    
    # We might need to split requests if days_back is large, 
    # but FitBark usually allows up to a month in one call.
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)
    
    raw_data = await fetch_fitbark_data(
        external_id, 
        access_token, 
        start_date.isoformat(), 
        end_date.isoformat()
    )
    
    if raw_data == "UNAUTHORIZED":
        # Retry once after refresh
        device = await refresh_fitbark_token(device)
        if device:
             raw_data = await fetch_fitbark_data(external_id, device["access_token"], start_date.isoformat(), end_date.isoformat())
    
    if not raw_data or raw_data == "UNAUTHORIZED":
        return
    
    normalized_data = normalize_data("fitbark", raw_data)
    
    # Use a set to track what we've already processed in this batch to reduce DB calls
    # but since we are doing simple query_db per point, we just let it run.
    # Optimization: bulk insert if supported by team-db.
    
    for item in normalized_data:
        timestamp = item["timestamp"]
        data_type = item["type"]
        
        # Idempotent check
        existing = query_db(f"SELECT id FROM health_data WHERE pet_id = '{pet_id}' AND type = '{data_type}' AND timestamp = '{timestamp}'")
        
        if not existing:
            data_id = str(uuid.uuid4())
            value = item["value"]
            unit = item["unit"]
            device_id = device["id"]
            
            query_db(f"INSERT INTO health_data (id, pet_id, device_id, type, value, unit, timestamp) VALUES ('{data_id}', '{pet_id}', '{device_id}', '{data_type}', {value}, '{unit}', '{timestamp}')")
    
    # After ingestion, trigger anomaly detection
    await run_anomaly_detection_for_pet(pet_id)

async def sync_all_devices():
    """
    Periodic task to sync all connected FitBark devices.
    """
    devices = query_db("SELECT * FROM devices WHERE type = 'fitbark'")
    for device in devices:
        await sync_fitbark_device(device)
