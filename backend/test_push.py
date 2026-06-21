import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_push_token():
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
    
    # 2. Register token
    push_data = {
        "token": "exponent-push-token-123",
        "platform": "ios"
    }
    response = httpx.post(f"{BASE_URL}/notifications/register-token", json=push_data, headers=headers)
    print(f"Register Token Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 3. Unregister token
    response = httpx.delete(f"{BASE_URL}/notifications/unregister-token/exponent-push-token-123", headers=headers)
    print(f"Unregister Token Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_push_token()
