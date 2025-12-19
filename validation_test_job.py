"""
Validation Test - Create a single follow job for testing
"""

from models import Job, DonatedAccount, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import time

# Connect to database
engine = create_engine('sqlite:///barter.db')
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 70)
print("🧪 VALIDATION TEST - JOB CREATION")
print("=" * 70)
print()

# Get or create test user
user = session.query(User).filter_by(email='validation@test.com').first()
if not user:
    user = User(
        email='validation@test.com',
        session_id='validation-session',
        is_authenticated=True,
        free_test_used=False
    )
    session.add(user)
    session.commit()
    print(f"✅ Created test user: {user.email}")
else:
    print(f"✅ Using existing test user: {user.email}")

# Get donor accounts
accounts = session.query(DonatedAccount).filter_by(status='unused').all()
print(f"📊 Available donor accounts: {len(accounts)}")
for acc in accounts:
    print(f"   - @{acc.username} (status: {acc.status})")

if len(accounts) == 0:
    print("❌ ERROR: No donor accounts available!")
    session.close()
    exit(1)

print()

# Create job
accounts_data = [
    {'username': acc.username, 'password': acc.password, 'id': acc.id}
    for acc in accounts
]

job = Job(
    job_type='follow',
    target_username='instagram',
    tier='free_test',
    user_id=user.id,
    payload={'accounts': accounts_data},
    status='pending',
    created_at=datetime.utcnow()
)

session.add(job)
session.commit()

print(f"✅ JOB CREATED:")
print(f"   Job ID: #{job.id}")
print(f"   Type: {job.job_type}")
print(f"   Target: @{job.target_username}")
print(f"   Tier: {job.tier}")
print(f"   Status: {job.status}")
print(f"   Donor Accounts: {len(accounts_data)}")
print(f"   Created: {job.created_at}")
print()

# Monitor job status
print("🔍 MONITORING JOB STATUS...")
print("   (Polling every 2 seconds for 60 seconds)")
print()

start_time = datetime.utcnow()
last_status = None
status_changes = []

for i in range(30):  # 60 seconds total
    time.sleep(2)
    session.expire_all()
    
    job = session.query(Job).filter_by(id=job.id).first()
    
    if job.status != last_status:
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        status_changes.append({
            'status': job.status,
            'time': elapsed,
            'started_at': job.started_at,
            'completed_at': job.completed_at
        })
        
        print(f"[{elapsed:.1f}s] Status: {job.status.upper()}")
        if job.started_at and not last_status:
            print(f"        Started at: {job.started_at}")
        if job.completed_at:
            print(f"        Completed at: {job.completed_at}")
            print(f"        Result: {job.result}")
            if job.error:
                print(f"        Error: {job.error}")
        
        last_status = job.status
        
        if job.status in ['complete', 'failed']:
            print()
            print("✅ Job finished!")
            break

print()
print("=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print(f"Job ID: #{job.id}")
print(f"Final Status: {job.status}")
print(f"Status Transitions: {len(status_changes)}")
for change in status_changes:
    print(f"  - {change['status']} at {change['time']:.1f}s")

print()
print(f"Execution Time: {(datetime.utcnow() - start_time).total_seconds():.1f}s")
print()

# Check donor account status
print("🔍 DONOR ACCOUNT STATUS:")
for acc in accounts:
    session.expire(acc)
    session.refresh(acc)
    print(f"   @{acc.username}: {acc.status}")

print()
session.close()
