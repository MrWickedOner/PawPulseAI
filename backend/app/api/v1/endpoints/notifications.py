from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from datetime import datetime

from .auth import get_current_user
from ....db.base import query_db, escape_string
from ....models.schemas import PushToken, PushTokenCreate

router = APIRouter()

@router.post("/register-token", response_model=PushToken)
async def register_push_token(
    token_in: PushTokenCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Register a push notification token for the current user.
    """
    # If this token exists for ANY user, delete it first (to reassign to current user)
    # This handles the case where a device changes owners or users
    query_db(f"DELETE FROM push_tokens WHERE token = '{escape_string(token_in.token)}'")
    
    # Create new registration
    token_id = str(uuid.uuid4())
    query_db(f"""
        INSERT INTO push_tokens (id, user_id, token, platform) 
        VALUES ('{token_id}', '{current_user['id']}', '{escape_string(token_in.token)}', '{escape_string(token_in.platform)}')
    """)
    
    new_token = query_db(f"SELECT * FROM push_tokens WHERE id = '{token_id}'")[0]
    return new_token

@router.delete("/unregister-token/{token}")
async def unregister_push_token(
    token: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Unregister a push notification token.
    """
    query_db(f"DELETE FROM push_tokens WHERE user_id = '{current_user['id']}' AND token = '{escape_string(token)}'")
    return {"status": "success"}
