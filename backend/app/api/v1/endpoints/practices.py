from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import datetime

from .auth import get_current_user
from ....db.base import query_db, escape_string
from ....models.schemas import Practice, PracticeCreate, Pet

router = APIRouter()

def check_pro_tier(user: dict):
    if user.get("tier") != "pro":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail="Pro tier subscription required for this action."
        )

@router.post("/", response_model=Practice)
def register_practice(
    practice_in: PracticeCreate, 
    current_user: dict = Depends(get_current_user)
):
    check_pro_tier(current_user)
    
    practice_id = str(uuid.uuid4())
    name = escape_string(practice_in.name)
    address = escape_string(practice_in.address)
    license_info = escape_string(practice_in.license_info)
    
    query_db(f"INSERT INTO practices (id, owner_id, name, address, license_info) VALUES ('{practice_id}', '{current_user['id']}', '{name}', '{address}', '{license_info}')")
    
    practice = query_db(f"SELECT * FROM practices WHERE id = '{practice_id}'")[0]
    return practice

@router.get("/my", response_model=List[Practice])
def get_my_practices(current_user: dict = Depends(get_current_user)):
    check_pro_tier(current_user)
    return query_db(f"SELECT * FROM practices WHERE owner_id = '{current_user['id']}'")

@router.post("/{practice_id}/patients/{pet_id}")
def add_patient_to_practice(
    practice_id: str, 
    pet_id: str, 
    current_user: dict = Depends(get_current_user)
):
    check_pro_tier(current_user)
    
    # Check practice ownership
    practice = query_db(f"SELECT * FROM practices WHERE id = '{practice_id}' AND owner_id = '{current_user['id']}'")
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found or not owned by you.")
    
    # Check if patient exists
    pet = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}'")
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found.")
    
    # Check if already added
    existing = query_db(f"SELECT * FROM practice_patients WHERE practice_id = '{practice_id}' AND pet_id = '{pet_id}'")
    if existing:
        return {"message": "Patient already added to practice."}
        
    pp_id = str(uuid.uuid4())
    query_db(f"INSERT INTO practice_patients (id, practice_id, pet_id) VALUES ('{pp_id}', '{practice_id}', '{pet_id}')")
    
    return {"message": "Patient added to practice."}

@router.get("/{practice_id}/patients", response_model=List[Pet])
def list_practice_patients(
    practice_id: str, 
    current_user: dict = Depends(get_current_user)
):
    check_pro_tier(current_user)
    
    # Check practice ownership
    practice = query_db(f"SELECT * FROM practices WHERE id = '{practice_id}' AND owner_id = '{current_user['id']}'")
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found or not owned by you.")
    
    patients = query_db(f"""
        SELECT p.* FROM pets p
        JOIN practice_patients pp ON p.id = pp.pet_id
        WHERE pp.practice_id = '{practice_id}'
    """)
    return patients
