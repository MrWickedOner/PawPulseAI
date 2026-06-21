from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any

from .auth import get_current_user
from ....services.anomaly import run_anomaly_detection_for_pet, analysis_status
from ....db.base import query_db

router = APIRouter()

@router.post("/run/{pet_id}")
async def trigger_analysis(pet_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    # Check if pet belongs to user
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Run analysis (can be background or immediate, lead asked for POST so maybe immediate result is expected or at least triggered)
    # Lead's message: "Manual trigger: Add POST /api/v1/analysis/run/{pet_id} for on-demand analysis"
    # I'll run it immediately and return the result.
    result = await run_anomaly_detection_for_pet(pet_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Analysis failed")
    
    return result

@router.get("/status")
def get_analysis_status(current_user: dict = Depends(get_current_user)):
    # In a real app we might restrict this to admins, but for MVP we'll let users see it
    return analysis_status
