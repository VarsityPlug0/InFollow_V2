"""
Trigger First Instagram Follow Job
Creates a job and monitors execution with real-time observability
"""

import time
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, '.')
from models import Job, User, DonatedAccount, ActionLog

# Database setup
engine = create_engine('sqlite:///barter.db')
Session = sessionmaker(bind=engine)
db_session = Session()

print("=" * 70)
print("🚀 TRIGGERING FIRST INSTAGRAM FOLLOW JOB")
print("=" * 70)

# Step 1: Create job
print("\n[1/7] Creating job in Brain database...")

# Get user
user = db_session.query(User).filter_by(email='test.e2e@example.com').first()
if not user:
    print("❌ User not found. Creating new user...")
    user = User(email='test.e2e@example.com', session_id='test-session-001', is_authenticated=True)
    db_session.add(user)
    db_session.commit()
    print(f"✅ Created user: {user.email}")
else:
    print(f"✅ Found user: {user.email}")

# Get unused donor accounts
unused_accounts = db_session.query(DonatedAccount).filter_by(status='unused').all()
if not unused_accounts:
    print("❌ No unused accounts available!")
    exit(1)

print(f"✅ Found {len(unused_accounts)} unused donor account(s)")

# Prepare account data
accounts_data = [
    {'username': acc.username, 'password': acc.password, 'id': acc.id}
    for acc in unused_accounts
]

# Create job
job = Job(
    job_type='follow',
    target_username='instagram',
    tier='free_test',
    user_id=user.id,
    payload={'accounts': accounts_data},
    status='pending',
    created_at=datetime.utcnow()
)

db_session.add(job)
db_session.commit()

job_id = job.id
start_time = datetime.utcnow()

print(f"\n✅ JOB CREATED:")
print(f"   Job ID: #{job_id}")
print(f"   Type: {job.job_type}")
print(f"   Target: @{job.target_username}")
print(f"   Tier: {job.tier}")
print(f"   Donor Accounts: {len(accounts_data)}")
print(f"   Status: {job.status}")
print(f"   Created: {job.created_at}")

for i, acc in enumerate(accounts_data, 1):
    print(f"   Workforce [{i}]: @{acc['username']}")

# Step 2: Monitor job execution
print("\n[2/7] Hands worker should pick up job within 5 seconds...")
print("⏱️  Monitoring job status (max 60 seconds)...\n")

status_emojis = {
    'pending': '⏳',
    'processing': '⚙️ ',
    'complete': '✅',
    'failed': '❌'
}

last_status = 'pending'
retry_count = 0
max_retries = 1

for i in range(60):
    time.sleep(1)
    
    # Refresh job from database
    db_session.expire_all()
    job = db_session.query(Job).filter_by(id=job_id).first()
    
    if job.status != last_status:
        emoji = status_emojis.get(job.status, '❓')
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        print(f"[{elapsed:.1f}s] {emoji} Job #{job.id}: {job.status.upper()}")
        
        if job.status == 'processing':
            print(f"        💪 Workforce activated: {len(accounts_data)} account(s)")
            if job.started_at:
                print(f"        🕐 Started: {job.started_at}")
        
        last_status = job.status
    
    # Check for completion or failure
    if job.status == 'complete':
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print("✅ JOB COMPLETED SUCCESSFULLY!")
        print(f"{'='*70}")
        
        # Step 3-4: Brain and Hands logs (already captured in terminals)
        print("\n[3/7] Brain logs - Check Terminal 1 for:")
        print("      ✓ [INTERNAL] Job sent to Hands")
        print("      ✓ [INTERNAL] Progress updates")
        print("      ✓ [INTERNAL] Job completion")
        
        print("\n[4/7] Hands logs - Check Terminal 2 for:")
        print("      ✓ Job received notification")
        print("      ✓ Workforce allocation")
        print("      ✓ Follow execution steps")
        print("      ✓ Completion message")
        
        # Step 5: Verify job in database
        print("\n[5/7] Verifying job in database...")
        print(f"      ✅ Job status: {job.status}")
        print(f"      ✅ Started at: {job.started_at}")
        print(f"      ✅ Completed at: {job.completed_at}")
        
        # Step 6: Print summary
        print(f"\n[6/7] JOB EXECUTION SUMMARY:")
        print(f"{'='*70}")
        print(f"  Job ID:          #{job_id}")
        print(f"  Target:          @{job.target_username}")
        print(f"  Donor Account:   @{accounts_data[0]['username']}")
        print(f"  Execution Time:  {execution_time:.2f} seconds")
        print(f"  Status:          {job.status.upper()} ✅")
        
        if job.result:
            result = job.result
            print(f"\n  Results:")
            print(f"    Total Accounts:  {result.get('total', 0)}")
            print(f"    Success:         {result.get('success', 0)}")
            print(f"    Failed:          {result.get('failed', 0)}")
            print(f"    Already Follow:  {result.get('already_followed', 0)}")
        
        # Check action logs
        print(f"\n[7/7] Checking action logs...")
        action_logs = db_session.query(ActionLog).filter_by(target=job.target_username).all()
        if action_logs:
            print(f"      ✅ Found {len(action_logs)} action log(s)")
            for log in action_logs:
                print(f"         @{log.donor_account} → @{log.target}: {log.result}")
        else:
            print(f"      ⚠️  No action logs found")
        
        # Check donor account status
        donor = db_session.query(DonatedAccount).filter_by(id=accounts_data[0]['id']).first()
        if donor:
            print(f"\n  Donor Account Status:")
            print(f"    Username:   @{donor.username}")
            print(f"    Status:     {donor.status}")
            print(f"    Tier Used:  {donor.tier_used or 'N/A'}")
            print(f"    Used At:    {donor.used_at or 'N/A'}")
        
        print(f"\n{'='*70}")
        print("🎉 FIRST JOB EXECUTION COMPLETE!")
        print(f"{'='*70}")
        print("\n💡 Next Steps:")
        print("   • Check both terminal logs for detailed execution trace")
        print("   • Open http://localhost:5000/admin (password: admin123)")
        print("   • View action logs and account status")
        print("   • Test via browser UI for Socket.IO real-time updates")
        
        break
    
    elif job.status == 'failed':
        print(f"\n{'='*70}")
        print("❌ JOB FAILED")
        print(f"{'='*70}")
        
        if job.error:
            print(f"  Error: {job.error}")
        
        # Step 7: Retry once if failed
        if retry_count < max_retries:
            retry_count += 1
            print(f"\n[7/7] RETRY ATTEMPT {retry_count}/{max_retries}")
            print("      Resetting job status to 'pending'...")
            
            job.status = 'pending'
            job.started_at = None
            job.completed_at = None
            job.error = None
            db_session.commit()
            
            print("      ✅ Job reset. Waiting for Hands worker...")
            start_time = datetime.utcnow()
            last_status = 'pending'
            continue
        else:
            print(f"\n  Max retries ({max_retries}) reached.")
            print("\n[6/7] FAILURE SUMMARY:")
            print(f"{'='*70}")
            print(f"  Job ID:          #{job_id}")
            print(f"  Target:          @{job.target_username}")
            print(f"  Donor Account:   @{accounts_data[0]['username']}")
            print(f"  Status:          {job.status.upper()} ❌")
            print(f"  Error:           {job.error or 'Unknown error'}")
            
            break

else:
    # Timeout after 60 seconds
    print(f"\n{'='*70}")
    print("⏱️  TIMEOUT: Job not completed within 60 seconds")
    print(f"{'='*70}")
    print(f"  Current Status: {job.status}")
    print(f"\n  Possible Issues:")
    print(f"    • Hands worker not polling")
    print(f"    • Worker crashed or stuck")
    print(f"    • Network connectivity issues")
    print(f"\n  Troubleshooting:")
    print(f"    1. Check Hands worker terminal for errors")
    print(f"    2. Verify Brain is responding: curl http://localhost:5000/internal/poll-jobs")
    print(f"    3. Restart Hands worker if needed")

db_session.close()
