from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from ...core.security import get_current_user
from ...models.schemas import PushTokenCreate
from ...db.base import team_db
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/push-token")
async def register_push_token(
    token_data: PushTokenCreate,
    current_user: Any = Depends(get_current_user)
) -> Any:
    """
    Register a push notification token for the current user.
    Handles upsert (same token -> update, new token -> insert).
    """
    user_id = current_user["id"]
    token = token_data.token
    platform = token_data.platform or "unknown"

    try:
        # Check if the token already exists
        existing = team_db(f"SELECT id, user_id FROM push_tokens WHERE token = '{token}'")
        
        if existing:
            # If it exists, update the user_id and platform
            # (handles reassignment if another user logs into the same device)
            token_id = existing[0]["id"]
            team_db(f"UPDATE push_tokens SET user_id = '{user_id}', platform = '{platform}' WHERE id = '{token_id}'")
            logger.info(f"Updated push token {token_id} for user {user_id}")
        else:
            # Insert new token
            token_id = str(uuid.uuid4())
            team_db(f"INSERT INTO push_tokens (id, user_id, token, platform) VALUES ('{token_id}', '{user_id}', '{token}', '{platform}')")
            logger.info(f"Registered new push token {token_id} for user {user_id}")

        return {"success": True}
    except Exception as e:
        logger.error(f"Error registering push token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
