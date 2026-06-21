from fastapi import HTTPException, status, Depends
from .endpoints.auth import get_current_user

def check_tier(required_tier: str):
    def tier_dependency(current_user: dict = Depends(get_current_user)):
        user_tier = current_user.get("tier", "free")
        
        # Simple hierarchy: free < basic < premium < pro
        tier_hierarchy = {"free": 0, "basic": 1, "premium": 2, "pro": 3}
        
        if tier_hierarchy.get(user_tier, 0) < tier_hierarchy.get(required_tier, 0):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"{required_tier.capitalize()} tier subscription required for this action."
            )
        return current_user
    return tier_dependency
