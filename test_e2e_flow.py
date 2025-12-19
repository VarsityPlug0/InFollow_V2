"""
End-to-End Test Script
Creates a test job and monitors execution through Brain/Hands architecture
"""

import requests
import time
import json

BRAIN_URL = "http://localhost:5000"

print("=" * 60)
print("🧪 END-TO-END TEST: Brain/Hands Job Flow")
print("=" * 60)

# Step 1: Create a test user session
print("\n[1/5] Creating test user session...")
session = requests.Session()

# Access homepage to create session
response = session.get(f"{BRAIN_URL}/")
if response.status_code == 200:
    print("✅ Session created")
    cookies = session.cookies.get_dict()
    print(f"    Session cookies: {list(cookies.keys())}")
else:
    print(f"❌ Failed to create session: {response.status_code}")
    exit(1)

# Step 2: Sign up with test email
print("\n[2/5] Signing up test user...")
signup_data = {
    "email": "test.e2e@example.com",
    "instagram": "test_target_user"
}

response = session.post(
    f"{BRAIN_URL}/api/signup",
    json=signup_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ User signed up: {result.get('email')}")
else:
    print(f"⚠️  Signup response: {response.status_code}")
    print(f"    {response.text[:200]}")

# Step 3: Look up target profile first
print("\n[3/5] Looking up target profile...")
lookup_data = {
    "username": "instagram"  # Using Instagram's official account as test
}

response = session.post(
    f"{BRAIN_URL}/api/lookup-profile",
    json=lookup_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Profile found: @{result.get('username')}")
    print(f"    Full name: {result.get('full_name')}")
    print(f"    Followers: {result.get('follower_count')}")
else:
    print(f"⚠️  Lookup response: {response.status_code}")
    print(f"    {response.text[:200]}")

# Step 4: Claim free followers (triggers job creation)
print("\n[4/5] Claiming free followers (creating job)...")
claim_data = {}

response = session.post(
    f"{BRAIN_URL}/api/claim-free-followers",
    json=claim_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Job created!")
    print(f"    Target: @{result.get('target')}")
    print(f"    Job ID: {result.get('job_id')}")
    print(f"    Message: {result.get('message')}")
    job_id = result.get('job_id')
else:
    print(f"❌ Failed to create job: {response.status_code}")
    print(f"    {response.text}")
    exit(1)

# Step 5: Monitor job status in database
print("\n[5/5] Monitoring job execution...")
print("    (Hands worker should pick up the job within 5 seconds)")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///barter.db')
Session = sessionmaker(bind=engine)
db_session = Session()

# Import models
import sys
sys.path.insert(0, '.')
from models import Job

for i in range(20):  # Check for up to 20 seconds
    time.sleep(1)
    job = db_session.query(Job).filter_by(id=job_id).first()
    
    if job:
        status_emoji = {
            'pending': '⏳',
            'processing': '⚙️',
            'complete': '✅',
            'failed': '❌'
        }.get(job.status, '❓')
        
        print(f"    [{i+1}s] {status_emoji} Job #{job.id}: {job.status}")
        
        if job.status == 'complete':
            print(f"\n✅ Job completed successfully!")
            if job.result:
                print(f"    Result: {json.dumps(job.result, indent=2)}")
            break
        elif job.status == 'failed':
            print(f"\n❌ Job failed!")
            if job.error:
                print(f"    Error: {job.error}")
            break
    else:
        print(f"    [{i+1}s] ❓ Job not found in database")

# Step 6: Verify results
print("\n[6/6] Verifying results...")

job = db_session.query(Job).filter_by(id=job_id).first()
if job:
    print(f"✅ Job #{job.id} final status: {job.status}")
    print(f"    Type: {job.job_type}")
    print(f"    Target: @{job.target_username}")
    print(f"    Tier: {job.tier}")
    print(f"    Created: {job.created_at}")
    print(f"    Started: {job.started_at}")
    print(f"    Completed: {job.completed_at}")
    
    if job.result:
        print(f"\n📊 Job Results:")
        result = job.result
        print(f"    Success: {result.get('success_count', 0)}")
        print(f"    Failed: {result.get('failed_count', 0)}")
        print(f"    Total: {result.get('total_accounts', 0)}")
else:
    print(f"❌ Job not found")

db_session.close()

print("\n" + "=" * 60)
print("✅ END-TO-END TEST COMPLETE")
print("=" * 60)
print("\n💡 Check the terminal logs:")
print("   - Brain Terminal: Job creation & internal API calls")
print("   - Hands Terminal: Job execution & Instagram actions")
