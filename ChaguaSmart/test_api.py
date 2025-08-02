import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

# Test data
test_user = {
    'username': 'teststudent',
    'email': 'student@test.com',
    'password': 'testpass123',
    'campus': 'Main'
}

# Test registration (if you have this endpoint)
try:
    response = requests.post(f'{BASE_URL}/api/auth/register/', json=test_user)
    print(f"Registration: {response.status_code}")
except:
    print("Registration endpoint not available yet")

# Test admin login
try:
    login_data = {
        'username': 'admin',  # Use your superuser credentials
        'password': 'your_admin_password'
    }
    response = requests.post(f'{BASE_URL}/api/token/', json=login_data)
    if response.status_code == 200:
        token = response.json()['access']
        print(f"Login successful, token: {token[:20]}...")
    else:
        print(f"Login failed: {response.status_code}")
except Exception as e:
    print(f"Login test failed: {e}")