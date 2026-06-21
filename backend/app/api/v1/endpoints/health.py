from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import datetime, timedelta

from .auth import get_current_user
from ..dependencies import check_tier
from ....db.base import query_db, escape_string
from ....models.schemas import HealthDataCreate, HealthData

router = APIRouter()

@router.post("/", response_model=HealthData)
def create_health_data(data_in: HealthDataCreate, current_user: dict = Depends(get_current_user)):
    # Check if pet belongs to user (or if this is called by an internal ingestion service)
    # For now, we assume this endpoint might be used by the ingestion pipeline or AI engine
    pets = query_db(f"SELECT * FROM pets WHERE id = '{data_in.pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
         # Check if it's a "system" request? For MVP, we just check ownership.
         # In a real app, ingestion might have a different auth.
         raise HTTPException(status_code=404, detail="Pet not found or not owned by user")
    
    data_id = str(uuid.uuid4())
    type = escape_string(data_in.type)
    value = data_in.value
    unit = escape_string(data_in.unit)
    timestamp = data_in.timestamp.isoformat()
    
    query_db(f"INSERT INTO health_data (id, pet_id, device_id, type, value, unit, timestamp) VALUES ('{data_id}', '{data_in.pet_id}', '{data_in.device_id}', '{type}', {value}, '{unit}', '{timestamp}')")
    
    data = query_db(f"SELECT * FROM health_data WHERE id = '{data_id}'")[0]
    return data

@router.get("/{pet_id}", response_model=List[HealthData])
def read_health_data(pet_id: str, current_user: dict = Depends(get_current_user)):
    # Check ownership
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
        
    # Tier enforcement for data history
    user_tier = current_user.get("tier", "free")
    if user_tier == "free":
        # Free users only get last 24 hours
        since = (datetime.utcnow() - timedelta(days=1)).isoformat()
        data = query_db(f"SELECT * FROM health_data WHERE pet_id = '{pet_id}' AND timestamp >= '{since}' ORDER BY timestamp DESC")
    elif user_tier == "basic":
        # Basic users get last 7 days
        since = (datetime.utcnow() - timedelta(days=7)).isoformat()
        data = query_db(f"SELECT * FROM health_data WHERE pet_id = '{pet_id}' AND timestamp >= '{since}' ORDER BY timestamp DESC")
    else:
        # Premium and Pro get full history
        data = query_db(f"SELECT * FROM health_data WHERE pet_id = '{pet_id}' ORDER BY timestamp DESC")
        
    return data
