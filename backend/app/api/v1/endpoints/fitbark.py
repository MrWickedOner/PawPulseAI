from fastapi import APIRouter, Depends, HTTPException, status
import httpx
import uuid
from datetime import datetime, timedelta

from .auth import get_current_user
from ....core.config import settings
from ....db.base import query_db, escape_string
from ....services.ingestion import sync_fitbark_device

router = APIRouter()

FITBARK_TOKEN_URL = "https://app.fitbark.com/oauth/token"
FITBARK_BASE_URL = "https://app.fitbark.com/api/v2"

@router.get("/callback")
async def fitbark_callback(code: str, state: str):
    pet_id = state
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            FITBARK_TOKEN_URL,
            data={
                "client_id": settings.FITBARK_CLIENT_ID,
                "client_secret": settings.FITBARK_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.FITBARK_REDIRECT_URI,
            },
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch token from FitBark")
        
        token_data = response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        token_type = token_data.get("token_type", "Bearer")
        
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        
        # Get external_id (dog slug)
        headers = {"Authorization": f"Token token={access_token}"}
        
        dog_response = await client.get(f"{FITBARK_BASE_URL}/dog_relations", headers=headers)
        if dog_response.status_code != 200:
             raise HTTPException(status_code=400, detail="Failed to fetch dogs from FitBark")
        
        dog_relations = dog_response.json().get("dog_relations", [])
        if not dog_relations:
             raise HTTPException(status_code=400, detail="No dogs found in FitBark account")
        
        # In a real app, we might let the user choose which dog to link if there are multiple.
        # For MVP, we'll link the first one.
        external_id = dog_relations[0]["dog"]["slug"]
        
        # Save or update device
        existing_devices = query_db(f"SELECT id FROM devices WHERE pet_id = '{pet_id}' AND type = 'fitbark'")
        
        if existing_devices:
            device_id = existing_devices[0]['id']
            query_db(f"UPDATE devices SET access_token = '{access_token}', refresh_token = '{refresh_token}', token_expires_at = '{expires_at}', token_type = '{token_type}', external_id = '{external_id}' WHERE id = '{device_id}'")
        else:
            device_id = str(uuid.uuid4())
            query_db(f"INSERT INTO devices (id, pet_id, type, external_id, access_token, refresh_token, token_expires_at, token_type) VALUES ('{device_id}', '{pet_id}', 'fitbark', '{external_id}', '{access_token}', '{refresh_token}', '{expires_at}', '{token_type}')")
            
        # Trigger initial 30-day sync
        device = query_db(f"SELECT * FROM devices WHERE id = '{device_id}'")[0]
        await sync_fitbark_device(device, days_back=30)
        
    return {"message": "FitBark connected and 30-day historical data synced successfully"}

@router.post("/sync/{pet_id}")
async def trigger_sync(pet_id: str, current_user: dict = Depends(get_current_user)):
    # Check if pet belongs to user
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
        
    devices = query_db(f"SELECT * FROM devices WHERE pet_id = '{pet_id}' AND type = 'fitbark'")
    if not devices:
        raise HTTPException(status_code=404, detail="FitBark device not connected for this pet")
        
    await sync_fitbark_device(devices[0])
    return {"message": "Sync completed"}
