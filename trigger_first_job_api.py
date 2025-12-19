"""
Trigger First Instagram Follow Job via Brain Internal API
Uses only standard Python libraries + requests
"""

import os
import sys
import time
import json
import requests
from datetime import datetime

# Configuration from environment variables
BRAIN_URL = os.environ.get('BRAIN_URL', 'http://localhost:5000')
HANDS_API_KEY = os.environ.get('HANDS_API_KEY', 'dev-hands-key-change-in-production')

# Job configuration
TARGET_USERNAME = 'instagram'
DONOR_ACCOUNT = {
    'username': 'virg.ildebie',
    'password': 'ShadowTest31@',
    'id': 1
}

def log(message):
    """Print with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

def create_job():
    """Create a follow job via Brain's internal API"""
    log("Creating follow job via Brain API...")
    
    headers = {
        'X-Hands-API-Key': HANDS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    job_data = {
        'job_type': 'follow',
        'target_username': TARGET_USERNAME,
        'tier': 'free_test',
        'user_id': 1,  # Test user ID
        'payload': {
            'accounts': [DONOR_ACCOUNT]
        },
        'status': 'pending'
    }
    
    try:
        # Note: This would require an endpoint to create jobs via API
        # For now, we'll poll for existing jobs
        log(f"⚠️  Note: Creating jobs requires database access")
        log(f"   Using existing job polling mechanism instead")
        return None
        
    except requests.exceptions.RequestException as e:
        log(f"❌ Error creating job: {str(e)}")
        return None

def poll_for_job():
    """Poll Brain for any pending job"""
    headers = {
        'X-Hands-API-Key': HANDS_API_KEY
    }
    
    try:
        response = requests.get(
            f"{BRAIN_URL}/internal/poll-jobs",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json().get('job')
        elif response.status_code == 204:
            return None
        else:
            log(f"⚠️  Poll returned HTTP {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        log(f"⚠️  Poll error: {str(e)}")
        return None

def check_job_status(job_id):
    """Check status of a specific job (requires a status endpoint)"""
    # This would need a dedicated endpoint in Brain
    # For now, we poll and check if the same job is returned
    return None

def main():
    """Main execution flow"""
    print("=" * 70)
    print("🎯 TRIGGER FIRST INSTAGRAM FOLLOW JOB")
    print("=" * 70)
    print()
    
    # Configuration summary
    log(f"Brain URL: {BRAIN_URL}")
    log(f"Target: @{TARGET_USERNAME}")
    log(f"Donor: @{DONOR_ACCOUNT['username']}")
    print()
    
    # Step 1: Check Brain connectivity
    log("Step 1: Testing Brain connectivity...")
    try:
        response = requests.get(f"{BRAIN_URL}/", timeout=5)
        if response.status_code == 200:
            log("✅ Brain is responding (HTTP 200)")
        else:
            log(f"⚠️  Brain returned HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        log(f"❌ Cannot connect to Brain: {str(e)}")
        log("   Make sure Brain is running: python app.py")
        sys.exit(1)
    
    print()
    
    # Step 2: Check Internal API
    log("Step 2: Testing Internal API authentication...")
    headers = {'X-Hands-API-KEY': HANDS_API_KEY}
    try:
        response = requests.get(
            f"{BRAIN_URL}/internal/poll-jobs",
            headers=headers,
            timeout=5
        )
        if response.status_code in [200, 204]:
            log(f"✅ Internal API authenticated (HTTP {response.status_code})")
        else:
            log(f"❌ API authentication failed (HTTP {response.status_code})")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        log(f"❌ Cannot access Internal API: {str(e)}")
        sys.exit(1)
    
    print()
    
    # Step 3: Look for existing pending jobs
    log("Step 3: Checking for pending jobs...")
    job = poll_for_job()
    
    if job:
        job_id = job['id']
        log(f"✅ Found pending job #{job_id}")
        log(f"   Type: {job['job_type']}")
        log(f"   Target: @{job['target_username']}")
        log(f"   Accounts: {len(job['payload']['accounts'])}")
    else:
        log("⚠️  No pending jobs found")
        log("")
        log("📋 To create a job, you need to:")
        log("   1. Access http://localhost:5000 in browser")
        log("   2. Sign up with an email")
        log("   3. Click 'Claim FREE Followers'")
        log("")
        log("   OR run: python trigger_first_job.py (database version)")
        print()
        log("💡 Waiting 60 seconds for a job to appear...")
        
        start_time = time.time()
        timeout = 60
        
        while time.time() - start_time < timeout:
            time.sleep(2)
            job = poll_for_job()
            
            if job:
                job_id = job['id']
                elapsed = time.time() - start_time
                log(f"✅ Job #{job_id} appeared after {elapsed:.1f}s!")
                log(f"   Type: {job['job_type']}")
                log(f"   Target: @{job['target_username']}")
                break
            else:
                elapsed = time.time() - start_time
                print(f"\r   [{elapsed:.0f}s] Still waiting...", end='', flush=True)
        else:
            print()
            log("⏱️  Timeout: No job appeared in 60 seconds")
            sys.exit(0)
    
    print()
    
    # Step 4: Monitor job execution
    log(f"Step 4: Monitoring job #{job_id} execution...")
    log("⏱️  Checking status every 2 seconds...")
    print()
    
    start_time = time.time()
    timeout = 60
    last_status = None
    
    while time.time() - start_time < timeout:
        # Poll to see if job is still pending (if it is, it hasn't been picked up yet)
        # If it's not returned, it means it was picked up and is processing/complete
        current_job = poll_for_job()
        
        if current_job and current_job['id'] == job_id:
            # Job still pending
            if last_status != 'pending':
                log("⏳ Job status: PENDING (waiting for Hands worker)")
                last_status = 'pending'
        else:
            # Job was picked up (no longer in pending queue)
            if last_status != 'processing':
                log("⚙️  Job status: PROCESSING (Hands worker executing)")
                last_status = 'processing'
            
            # In a real implementation, we'd check a status endpoint
            # For now, we'll assume processing completed after not seeing it
            elapsed = time.time() - start_time
            if elapsed > 10:  # If it's been processing for 10+ seconds
                log("✅ Job likely completed (no longer in queue)")
                break
        
        time.sleep(2)
    
    print()
    
    # Step 5: Summary
    execution_time = time.time() - start_time
    
    log("Step 5: Execution Summary")
    print("=" * 70)
    print(f"  Job ID:          #{job_id}")
    print(f"  Target:          @{job['target_username']}")
    print(f"  Accounts Used:   {len(job['payload']['accounts'])}")
    print(f"  Donor Account:   @{job['payload']['accounts'][0]['username']}")
    print(f"  Execution Time:  {execution_time:.2f} seconds")
    print(f"  Final Status:    {last_status.upper() if last_status else 'UNKNOWN'}")
    print("=" * 70)
    print()
    
    log("💡 To verify completion:")
    log("   1. Check Hands worker terminal for execution logs")
    log("   2. Check Brain terminal for job completion")
    log("   3. Run: python -c \"from models import Job; ...\" (database check)")
    print()
    
    log("✅ Monitoring complete!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        log("⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print()
        log(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
