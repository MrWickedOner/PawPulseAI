from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from .auth import get_current_user
from ....db.base import query_db, escape_string
from ....models.schemas import DeviceCreate, Device

router = APIRouter()

@router.post("/", response_model=Device)
def create_device(device_in: DeviceCreate, current_user: dict = Depends(get_current_user)):
    # Check if pet belongs to user
    pets = query_db(f"SELECT * FROM pets WHERE id = '{device_in.pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    device_id = str(uuid.uuid4())
    type = escape_string(device_in.type)
    external_id = escape_string(device_in.external_id)
    access_token = escape_string(device_in.access_token)
    refresh_token = escape_string(device_in.refresh_token) if device_in.refresh_token else "NULL"
    
    refresh_token_val = f"'{refresh_token}'" if refresh_token != "NULL" else "NULL"
    
    query_db(f"INSERT INTO devices (id, pet_id, type, external_id, access_token, refresh_token) VALUES ('{device_id}', '{device_in.pet_id}', '{type}', '{external_id}', '{access_token}', {refresh_token_val})")
    
    device = query_db(f"SELECT * FROM devices WHERE id = '{device_id}'")[0]
    return device

@router.get("/", response_model=List[Device])
def read_devices(current_user: dict = Depends(get_current_user)):
    # Join with pets to ensure ownership
    devices = query_db(f"SELECT d.* FROM devices d JOIN pets p ON d.pet_id = p.id WHERE p.owner_id = '{current_user['id']}'")
    return devices
