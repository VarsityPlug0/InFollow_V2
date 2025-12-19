"""
Test script to verify Brain/Hands setup
Run this before starting the actual worker
"""

import os
import sys
import requests

def test_environment():
    """Test environment variables"""
    print("\n" + "="*60)
    print("🔧 TESTING ENVIRONMENT VARIABLES")
    print("="*60)
    
    required_vars = [
        'BRAIN_URL',
        'HANDS_API_KEY',
        'DATABASE_URL',
        'SYSTEM_IG_USERNAME',
        'SYSTEM_IG_PASSWORD'
    ]
    
    missing = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask passwords
            if 'PASSWORD' in var or 'KEY' in var:
                display = value[:4] + '***' if len(value) > 4 else '***'
            else:
                display = value
            print(f"✓ {var}: {display}")
        else:
            print(f"✗ {var}: NOT SET")
            missing.append(var)
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print(f"\n✅ All environment variables set")
        return True

def test_brain_connection():
    """Test connection to Brain"""
    print("\n" + "="*60)
    print("🧠 TESTING BRAIN CONNECTION")
    print("="*60)
    
    brain_url = os.environ.get('BRAIN_URL', 'http://localhost:5000')
    hands_api_key = os.environ.get('HANDS_API_KEY', 'dev-hands-key-change-in-production')
    
    try:
        # Test poll endpoint
        response = requests.get(
            f"{brain_url}/internal/poll-jobs",
            headers={'X-Hands-API-Key': hands_api_key},
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print(f"✓ Brain reachable at {brain_url}")
            print(f"✓ API authentication successful")
            if response.status_code == 204:
                print(f"✓ No pending jobs (expected)")
            else:
                print(f"✓ Job available: {response.json()}")
            return True
        elif response.status_code == 401:
            print(f"✗ Authentication failed - check HANDS_API_KEY")
            print(f"  Brain expects different API key")
            return False
        else:
            print(f"✗ Unexpected response: HTTP {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {brain_url}")
        print(f"  Is Brain running?")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_database():
    """Test database connection"""
    print("\n" + "="*60)
    print("🗄️  TESTING DATABASE CONNECTION")
    print("="*60)
    
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///barter.db')
    
    # Fix Postgres URL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test query
            result = conn.execute(text("SELECT 1"))
            print(f"✓ Database connection successful")
            
            # Check tables exist
            if 'sqlite' in database_url:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            else:
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public';"))
            
            tables = [row[0] for row in result]
            expected_tables = ['users', 'donated_accounts', 'targets', 'action_logs', 'jobs']
            
            missing = [t for t in expected_tables if t not in tables]
            if missing:
                print(f"⚠️  Missing tables: {', '.join(missing)}")
                print(f"  Run migrations on Brain first")
            else:
                print(f"✓ All required tables exist")
            
            return len(missing) == 0
    
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        return False

def test_instagram_imports():
    """Test Instagram automation imports"""
    print("\n" + "="*60)
    print("📸 TESTING INSTAGRAM AUTOMATION")
    print("="*60)
    
    try:
        from instagram import InstagramAutomation
        from instagrapi import Client
        print(f"✓ instagram.py imported successfully")
        print(f"✓ instagrapi library available")
        
        ig = InstagramAutomation(session_folder='sessions')
        print(f"✓ InstagramAutomation initialized")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {str(e)}")
        print(f"  Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_models_imports():
    """Test models imports"""
    print("\n" + "="*60)
    print("📊 TESTING DATABASE MODELS")
    print("="*60)
    
    try:
        from models import db, User, DonatedAccount, Target, ActionLog, Job
        print(f"✓ models.py imported successfully")
        print(f"✓ All models available: User, DonatedAccount, Target, ActionLog, Job")
        return True
    except ImportError as e:
        print(f"✗ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 HANDS WORKER SETUP TEST")
    print("="*60)
    
    tests = [
        ("Environment", test_environment),
        ("Brain Connection", test_brain_connection),
        ("Database", test_database),
        ("Instagram Imports", test_instagram_imports),
        ("Models Imports", test_models_imports)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ {name} test crashed: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Ready to run hands_worker.py!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Fix issues before running worker")
        return 1

if __name__ == '__main__':
    sys.exit(main())
