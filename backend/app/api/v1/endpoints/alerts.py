from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from .auth import get_current_user
from ....db.base import query_db, escape_string
from ....models.schemas import AnomalyAlert, AnomalyAlertBase

router = APIRouter()

@router.post("/internal/push", response_model=AnomalyAlert)
def push_alert(alert_in: AnomalyAlertBase, pet_id: str):
    # This endpoint is intended for internal use by the AI/ML engine
    # In a real app, it would be secured by a secret API key or internal network policy.
    
    alert_id = str(uuid.uuid4())
    type = escape_string(alert_in.type)
    description = escape_string(alert_in.description)
    severity = escape_string(alert_in.severity)
    status = escape_string(alert_in.status)
    
    query_db(f"INSERT INTO anomaly_alerts (id, pet_id, type, description, severity, status) VALUES ('{alert_id}', '{pet_id}', '{type}', '{description}', '{severity}', '{status}')")
    
    alert = query_db(f"SELECT * FROM anomaly_alerts WHERE id = '{alert_id}'")[0]
    return alert

@router.get("/{pet_id}", response_model=List[AnomalyAlert])
def read_alerts(pet_id: str, current_user: dict = Depends(get_current_user)):
    # Check ownership
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
        
    alerts = query_db(f"SELECT * FROM anomaly_alerts WHERE pet_id = '{pet_id}' ORDER BY created_at DESC")
    return alerts

@router.post("/{pet_id}/acknowledge/{alert_id}")
def acknowledge_alert(pet_id: str, alert_id: str, current_user: dict = Depends(get_current_user)):
    # Check ownership
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
        
    query_db(f"UPDATE anomaly_alerts SET status = 'acknowledged' WHERE id = '{alert_id}' AND pet_id = '{pet_id}'")
    return {"message": "Alert acknowledged"}
