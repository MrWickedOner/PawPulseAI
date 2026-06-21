from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
import uuid
import logging
from datetime import datetime, timedelta

from .auth import get_current_user
from ....db.base import query_db, escape_string
from ....models.schemas import Subscription, CheckoutSessionCreate, CheckoutSession, SubscriptionTier, IAPVerification, IAPResponse
from ....services.receipt_validator import ReceiptValidator

router = APIRouter()
logger = logging.getLogger(__name__)

# Mock Stripe Service
class MockStripe:
    @staticmethod
    def create_checkout_session(user_id: str, tier: str, success_url: str, cancel_url: str):
        # In a real app, this would call stripe.checkout.Session.create
        session_id = str(uuid.uuid4())
        return f"https://checkout.stripe.com/pay/{session_id}?user_id={user_id}&tier={tier}&success_url={success_url}"

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str):
        # In a real app, this would call stripe.billing_portal.Session.create
        return f"https://billing.stripe.com/p/session/{customer_id}?return_url={return_url}"

@router.post("/create-checkout", response_model=CheckoutSession)
def create_checkout(
    checkout_in: CheckoutSessionCreate, 
    current_user: dict = Depends(get_current_user)
):
    checkout_url = MockStripe.create_checkout_session(
        user_id=current_user["id"],
        tier=checkout_in.tier,
        success_url=checkout_in.success_url,
        cancel_url=checkout_in.cancel_url
    )
    return {"checkout_url": checkout_url}

@router.post("/portal", response_model=CheckoutSession)
def create_portal(
    return_url: str, 
    current_user: dict = Depends(get_current_user)
):
    # Check if user has a stripe_customer_id
    sub = query_db(f"SELECT stripe_customer_id FROM subscriptions WHERE user_id = '{current_user['id']}' LIMIT 1")
    if not sub or not sub[0]["stripe_customer_id"]:
        # If no subscription, we might need to create a customer or handle differently
        # For mock, we'll just use a random ID
        customer_id = f"cus_{uuid.uuid4().hex[:8]}"
    else:
        customer_id = sub[0]["stripe_customer_id"]
        
    portal_url = MockStripe.create_portal_session(customer_id, return_url)
    return {"checkout_url": portal_url}

@router.get("/current", response_model=Subscription)
def get_current_subscription(current_user: dict = Depends(get_current_user)):
    sub = query_db(f"SELECT * FROM subscriptions WHERE user_id = '{current_user['id']}' ORDER BY created_at DESC LIMIT 1")
    if not sub:
        # Return a "free" subscription object if none found
        return {
            "id": "none",
            "user_id": current_user["id"],
            "tier": "free",
            "status": "active",
            "created_at": current_user["created_at"]
        }
    return sub[0]

# Mock Webhook for testing
@router.post("/webhook/mock")
async def mock_webhook(request: Request):
    # This simulates a Stripe webhook
    data = await request.json()
    event_type = data.get("type")
    
    if event_type == "subscription.created":
        user_id = data["user_id"]
        tier = data["tier"]
        stripe_sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        stripe_cus_id = f"cus_{uuid.uuid4().hex[:8]}"
        
        sub_id = str(uuid.uuid4())
        start = datetime.utcnow().isoformat()
        end = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        query_db(f"INSERT INTO subscriptions (id, user_id, tier, stripe_customer_id, stripe_subscription_id, status, current_period_start, current_period_end) VALUES ('{sub_id}', '{user_id}', '{tier}', '{stripe_cus_id}', '{stripe_sub_id}', 'active', '{start}', '{end}')")
        
        # Update user tier
        query_db(f"UPDATE users SET tier = '{tier}' WHERE id = '{user_id}'")
        
    return {"status": "success"}

@router.post("/verify-iap", response_model=IAPResponse)
async def verify_iap(
    verification: IAPVerification,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify an In-App Purchase receipt (iOS/Android) and upgrade user tier.
    """
    logger.info(f"Verifying IAP for user {current_user['id']} with product {verification.product_id} on {verification.platform}")
    
    # 1. Idempotency Check: See if this receipt has already been used
    # Note: In a real app, you'd want a hash or specific ID from the receipt info
    # For Apple, 'original_transaction_id' is a good candidate.
    # Since we don't have it yet, we might use the raw receipt data as a temporary check
    # or rely on the validator to provide it.
    
    # 2. Validate receipt
    try:
        result = await ReceiptValidator.validate(
            receipt_data=verification.receipt_data,
            platform=verification.platform,
            product_id=verification.product_id
        )
    except Exception as e:
        logger.exception("Receipt validation failed due to error")
        raise HTTPException(status_code=500, detail=f"Validation service error: {str(e)}")

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=f"Invalid receipt: {result.get('error')}")

    tier = result["tier"]
    expiry_date = result["expiry_date"]
    sub_id = result["subscription_id"]

    # Check for duplicate subscription_id (original_transaction_id)
    existing_sub = query_db(f"SELECT id FROM subscriptions WHERE iap_receipt_id = '{sub_id}' LIMIT 1")
    if existing_sub:
        logger.info(f"Receipt {sub_id} already processed for subscription {existing_sub[0]['id']}")
        # Return existing status (or update if needed, but usually once is enough for one transaction)
    else:
        # 3. Store subscription record
        internal_sub_id = str(uuid.uuid4())
        start = datetime.utcnow().isoformat()
        
        query_db(f"""
            INSERT INTO subscriptions (id, user_id, tier, status, current_period_start, current_period_end, iap_receipt_id) 
            VALUES ('{internal_sub_id}', '{current_user['id']}', '{tier}', 'active', '{start}', '{expiry_date}', '{sub_id}')
        """)
        
        # 4. Update user tier and expiry
        query_db(f"UPDATE users SET tier = '{tier}', subscription_expiry = '{expiry_date}' WHERE id = '{current_user['id']}'")
        logger.info(f"User {current_user['id']} upgraded to {tier} until {expiry_date}")

    return {
        "success": True,
        "tier": tier,
        "expiry_date": expiry_date,
        "subscription_id": sub_id
    }
