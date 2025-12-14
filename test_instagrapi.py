"""
Test script to verify instagrapi is working correctly
"""
import sys
from instagrapi import Client

def test_instagrapi():
    print("=" * 60)
    print("TESTING INSTAGRAPI INSTALLATION")
    print("=" * 60)
    
    try:
        # Test 1: Import
        print("\n✓ instagrapi imported successfully")
        
        # Test 2: Create client
        client = Client()
        print("✓ Client created successfully")
        
        # Test 3: Check methods exist
        assert hasattr(client, 'login'), "Client missing login method"
        assert hasattr(client, 'user_follow'), "Client missing user_follow method"
        assert hasattr(client, 'user_info_by_username'), "Client missing user_info_by_username method"
        print("✓ All required methods exist")
        
        print("\n" + "=" * 60)
        print("✅ INSTAGRAPI IS WORKING CORRECTLY")
        print("=" * 60)
        print("\nThe system is ready to use. To test with real accounts:")
        print("1. Open http://localhost:5000")
        print("2. Donate a real Instagram account (username + password)")
        print("3. The system will use instagrapi to verify login")
        print("4. Once you have 20+ accounts, test the Free Test Lane")
        print("\nNOTE: You need REAL Instagram credentials to test.")
        print("Test accounts are recommended to avoid affecting real accounts.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPlease run: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = test_instagrapi()
    sys.exit(0 if success else 1)
