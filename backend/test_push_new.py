import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_push_token_new_path():
    # 1. Login
    login_data = {"username": "demo@pawpulse.com", "password": "password123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Register push token on new path
    push_data = {
        "token": "ExpoPushToken[test-new-path]",
        "platform": "ios"
    }
    response = requests.post(f"{BASE_URL}/users/push-token", json=push_data, headers=headers)
    print(f"Register Token (New Path) Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 3. Register push token without platform (to test optionality)
    push_data_no_platform = {
        "token": "ExpoPushToken[test-no-platform]"
    }
    response = requests.post(f"{BASE_URL}/users/push-token", json=push_data_no_platform, headers=headers)
    print(f"Register Token (No Platform) Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_push_token_new_path()
