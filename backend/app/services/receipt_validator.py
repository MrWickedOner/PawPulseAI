import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)

class ReceiptValidator:
    @staticmethod
    async def validate(receipt_data: str, platform: str, product_id: str) -> Dict[str, Any]:
        """
        Validate a receipt with Apple or Google.
        Returns a dict with verification results.
        """
        mode = settings.IAP_VALIDATION_MODE
        
        if mode == "mock":
            return await ReceiptValidator._mock_validate(receipt_data, platform, product_id)
        
        if platform == "ios":
            return await ReceiptValidator._validate_apple(receipt_data)
        elif platform == "android":
            return await ReceiptValidator._validate_google(receipt_data, product_id)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    @staticmethod
    async def _mock_validate(receipt_data: str, platform: str, product_id: str) -> Dict[str, Any]:
        """
        Mock validation for testing without live credentials.
        """
        logger.info(f"MOCK validating {platform} receipt for {product_id}")
        
        # Simulate expiry: 30 days from now
        expiry_date = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
        
        return {
            "success": True,
            "tier": ReceiptValidator._get_tier_from_product(product_id),
            "expiry_date": expiry_date,
            "subscription_id": f"mock_sub_{uuid_short()}",
            "is_sandbox": True
        }

    @staticmethod
    async def _validate_apple(receipt_data: str) -> Dict[str, Any]:
        """
        Validate with Apple's verifyReceipt endpoint.
        Handles sandbox vs production environments.
        """
        # Apple Shared Secret should be in settings
        if not settings.APPLE_SHARED_SECRET and settings.IAP_VALIDATION_MODE != "mock":
            logger.error("APPLE_SHARED_SECRET not configured")
            return {"success": False, "error": "Server configuration error"}

        url = "https://buy.itunes.apple.com/verifyReceipt"
        payload = {
            "receipt-data": receipt_data,
            "password": settings.APPLE_SHARED_SECRET,
            "exclude-old-transactions": True
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                data = response.json()
                
                # Status 21007 means sandbox receipt sent to production
                if data.get("status") == 21007:
                    logger.info("Redirecting to Apple Sandbox for validation")
                    url = "https://sandbox.itunes.apple.com/verifyReceipt"
                    response = await client.post(url, json=payload, timeout=10.0)
                    data = response.json()
                
                status = data.get("status")
                if status == 0:
                    # Success
                    # Check for latest_receipt_info (for auto-renewable subscriptions)
                    receipt_info = data.get("latest_receipt_info", data.get("receipt", {}).get("in_app", []))
                    
                    if not receipt_info:
                        return {"success": False, "error": "No purchase found in receipt"}

                    if isinstance(receipt_info, list):
                        # Sort by expires_date_ms desc to get the latest state
                        receipt_info.sort(key=lambda x: int(x.get("expires_date_ms", 0)), reverse=True)
                        latest = receipt_info[0]
                    else:
                        latest = receipt_info
                    
                    product_id = latest.get("product_id")
                    expiry_ms = int(latest.get("expires_date_ms", 0))
                    
                    # Check if expired
                    if expiry_ms > 0 and expiry_ms < datetime.utcnow().timestamp() * 1000:
                        logger.warning(f"Apple receipt expired at {expiry_ms}")
                        # We might still return success but the caller should check expiry
                    
                    expiry_date = datetime.fromtimestamp(expiry_ms / 1000.0).isoformat() + "Z"
                    
                    return {
                        "success": True,
                        "tier": ReceiptValidator._get_tier_from_product(product_id),
                        "expiry_date": expiry_date,
                        "subscription_id": latest.get("original_transaction_id"),
                        "is_sandbox": data.get("environment") == "Sandbox"
                    }
                else:
                    error_msgs = {
                        21000: "App Store could not read the JSON object you provided.",
                        21002: "The data in the receipt-data property was malformed or missing.",
                        21003: "The receipt could not be authenticated.",
                        21004: "The shared secret you provided does not match the shared secret on file for your account.",
                        21005: "The receipt server is not currently available.",
                        21006: "This receipt is valid but the subscription has expired.",
                        21008: "This receipt is from the production environment, but it was sent to the test environment for verification.",
                        21010: "This receipt could not be authorized. Treat this the same as if a purchase was never made."
                    }
                    error_msg = error_msgs.get(status, f"Apple status {status}")
                    logger.error(f"Apple validation failed: {error_msg}")
                    return {"success": False, "error": error_msg}
            except httpx.RequestError as e:
                logger.error(f"Network error validating with Apple: {e}")
                return {"success": False, "error": "Could not connect to Apple validation server"}

    @staticmethod
    async def _validate_google(receipt_data: str, product_id: str) -> Dict[str, Any]:
        """
        Validate with Google Play Developer API.
        This usually requires a complex OAuth flow or service account.
        Structure provided here, implementation would use google-api-python-client.
        """
        # For now, if we don't have libraries, we'll keep it as a placeholder that fails
        # but is structured correctly.
        logger.warning("Google Play validation requested but not fully implemented (requires service account)")
        return {"success": False, "error": "Google Play validation not implemented"}

    @staticmethod
    def _get_tier_from_product(product_id: str) -> str:
        if "premium" in product_id.lower():
            return "premium"
        if "pro" in product_id.lower():
            return "pro"
        return "basic"

def uuid_short():
    import uuid
    return str(uuid.uuid4())[:8]
