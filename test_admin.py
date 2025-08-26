import requests

def test_admin_access():
    base_url = "http://localhost:5000"
    
    print("Testing admin panel accessibility...")
    
    # Test 1: Check if admin panel loads
    try:
        response = requests.get(f"{base_url}/admin/")
        print(f"Admin panel status: {response.status_code}")
    except Exception as e:
        print(f"Error accessing admin panel: {e}")
    
    # Test 2: Check user management
    try:
        response = requests.get(f"{base_url}/admin/user/")
        print(f"User management status: {response.status_code}")
    except Exception as e:
        print(f"Error accessing user management: {e}")
    
    # Test 3: Check video management
    try:
        response = requests.get(f"{base_url}/admin/video/")
        print(f"Video management status: {response.status_code}")
    except Exception as e:
        print(f"Error accessing video management: {e}")

if __name__ == "__main__":
    test_admin_access()
