import requests
import sys

try:
    print("Testing server at http://localhost:5000...")
    r = requests.get('http://localhost:5000', timeout=5)
    print(f"Status Code: {r.status_code}")
    
    if r.status_code == 200:
        print("✓ SUCCESS - Server is working!")
        if "Demo Mode" in r.text:
            print("✓ Demo mode detected in HTML")
        if "Instagram Barter System" in r.text:
            print("✓ Page title found")
    else:
        print(f"✗ ERROR - Server returned {r.status_code}")
        print("Response text (first 500 chars):")
        print(r.text[:500])
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR - Cannot connect to server")
    print("Make sure server is running: python app.py")
except Exception as e:
    print(f"✗ ERROR - {type(e).__name__}: {e}")
    sys.exit(1)
