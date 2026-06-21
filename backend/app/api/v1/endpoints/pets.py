from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from .auth import get_current_user
from ..dependencies import check_tier
from ....db.base import query_db, escape_string
from ....models.schemas import PetCreate, Pet
from ....core.config import settings

router = APIRouter()

FITBARK_AUTH_URL = "https://app.fitbark.com/oauth/authorize"

@router.get("/{pet_id}/report")
def get_pet_report(pet_id: str, current_user: dict = Depends(check_tier("premium"))):
    # Check ownership
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # In a real app, this would generate a PDF or a complex JSON report
    return {
        "pet_id": pet_id,
        "report_generated_at": datetime.utcnow(),
        "summary": "This is a premium health report summary.",
        "status": "Healthy",
        "recommendations": ["Maintain current activity levels", "Schedule next vet checkup in 3 months"]
    }

@router.post("/{pet_id}/devices/fitbark")
def initiate_fitbark_connect(pet_id: str, current_user: dict = Depends(get_current_user)):
    # Check if pet belongs to user
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    state = pet_id
    url = (
        f"{FITBARK_AUTH_URL}?"
        f"client_id={settings.FITBARK_CLIENT_ID}&"
        f"redirect_uri={settings.FITBARK_REDIRECT_URI}&"
        f"response_type=code&"
        f"state={state}"
    )
    return {"url": url}

@router.post("/", response_model=Pet)
def create_pet(pet_in: PetCreate, current_user: dict = Depends(get_current_user)):
    pet_id = str(uuid.uuid4())
    name = escape_string(pet_in.name)
    species = escape_string(pet_in.species)
    breed = escape_string(pet_in.breed) if pet_in.breed else "NULL"
    birth_date = escape_string(pet_in.birth_date) if pet_in.birth_date else "NULL"
    weight = pet_in.weight if pet_in.weight is not None else "NULL"
    
    owner_id = current_user["id"]
    
    # Handle NULLs properly in SQL string
    breed_val = f"'{breed}'" if breed != "NULL" else "NULL"
    birth_date_val = f"'{birth_date}'" if birth_date != "NULL" else "NULL"
    weight_val = f"{weight}" if weight != "NULL" else "NULL"
    
    query_db(f"INSERT INTO pets (id, owner_id, name, species, breed, birth_date, weight) VALUES ('{pet_id}', '{owner_id}', '{name}', '{species}', {breed_val}, {birth_date_val}, {weight_val})")
    
    pet = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}'")[0]
    return pet

@router.get("/", response_model=List[Pet])
def read_pets(current_user: dict = Depends(get_current_user)):
    pets = query_db(f"SELECT * FROM pets WHERE owner_id = '{current_user['id']}'")
    return pets

@router.get("/{pet_id}", response_model=Pet)
def read_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    pets = query_db(f"SELECT * FROM pets WHERE id = '{pet_id}' AND owner_id = '{current_user['id']}'")
    if not pets:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pets[0]
