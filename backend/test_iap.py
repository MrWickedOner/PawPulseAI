import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_iap():
    # 1. Login to get token
    login_data = {
        "username": "demo@pawpulse.com",
        "password": "demo123"
    }
    response = httpx.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Call verify-iap
    iap_data = {
        "receipt_data": "mock_receipt_base64_string",
        "product_id": "com.pawpulse.premium.monthly",
        "platform": "ios"
    }
    response = httpx.post(f"{BASE_URL}/subscriptions/verify-iap", json=iap_data, headers=headers)
    
    print(f"IAP Verification Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 3. Verify user tier in DB
    # (Checking current subscription endpoint)
    response = httpx.get(f"{BASE_URL}/subscriptions/current", headers=headers)
    print(f"Current Subscription: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_iap()
