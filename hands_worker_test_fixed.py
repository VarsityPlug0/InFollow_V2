"""
Test script to run Hands worker and capture logs for end-to-end testing
"""

import os
import sys
import time
import requests
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import instagram.py and models.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from instagram import InstagramAutomation
# Import table definitions directly to avoid Flask app initialization
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON

Base = declarative_base()

# Define minimal models for worker (avoid importing from models.py which triggers Flask app)
class DonatedAccount(Base):
    __tablename__ = 'donated_accounts'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    password = Column(String(200), nullable=False)
    status = Column(String(20), default='unused')
    tier_used = Column(String(20))
    user_id = Column(Integer, ForeignKey('users.id'))
    donated_at = Column(DateTime)
    used_at = Column(DateTime)

class ActionLog(Base):
    __tablename__ = 'action_logs'
    id = Column(Integer, primary_key=True)
    donor_account = Column(String(100), nullable=False)
    target = Column(String(100), nullable=False)
    tier = Column(String(20), nullable=False)
    result = Column(String(20), nullable=False)
    error = Column(Text)  # Added missing error column
    timestamp = Column(DateTime, default=datetime.utcnow)  # Fixed column name

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    target_username = Column(String(100))
    tier = Column(String(20))
    user_id = Column(Integer, ForeignKey('users.id'))
    payload = Column(JSON)
    result = Column(JSON)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error = Column(Text)

# Configuration
BRAIN_URL = os.environ.get('BRAIN_URL', 'http://localhost:5000')
HANDS_API_KEY = os.environ.get('HANDS_API_KEY', 'dev-hands-key-change-in-production')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///barter.db')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '5'))  # seconds
SYSTEM_IG_USERNAME = os.environ.get('SYSTEM_IG_USERNAME', 'virg.ildebie')
SYSTEM_IG_PASSWORD = os.environ.get('SYSTEM_IG_PASSWORD', 'ShadowTest31@')

# Fix Postgres URL if needed
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Database setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Instagram automation
ig_automation = InstagramAutomation(session_folder='sessions')

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def poll_for_job():
    """Poll Brain for pending jobs"""
    try:
        log(f"📡 Polling {BRAIN_URL}/internal/poll-jobs...")
        response = requests.get(
            f"{BRAIN_URL}/internal/poll-jobs",
            headers={'X-Hands-API-Key': HANDS_API_KEY},
            timeout=10
        )
        
        log(f"   Response: HTTP {response.status_code}")
        
        if response.status_code == 204:
            # No jobs available
            log("   No jobs available")
            return None
        elif response.status_code == 200:
            job_data = response.json().get('job')
            log(f"   Job received: #{job_data['id']} ({job_data['job_type']}) for @{job_data['target_username']}")
            return job_data
        else:
            log(f"⚠️ Poll failed: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        log(f"⚠️ Poll error: {str(e)}")
        return None

def send_progress(job_id, current, total, status_msg):
    """Send progress update to Brain"""
    try:
        log(f"📈 Sending progress for job #{job_id}: {current}/{total} - {status_msg}")
        response = requests.post(
            f"{BRAIN_URL}/internal/progress",
            json={
                'job_id': job_id,
                'current': current,
                'total': total,
                'status': status_msg
            },
            headers={'X-Hands-API-Key': HANDS_API_KEY},
            timeout=5
        )
        log(f"   Progress response: HTTP {response.status_code}")
    except Exception as e:
        log(f"⚠️ Progress update failed: {str(e)}")

def complete_job(job_id, status, result=None, error=None):
    """Mark job as complete in Brain"""
    try:
        log(f"✅ Completing job #{job_id} with status: {status}")
        if error:
            log(f"   Error: {error}")
        response = requests.post(
            f"{BRAIN_URL}/internal/job-complete",
            json={
                'job_id': job_id,
                'status': status,
                'result': result,
                'error': error
            },
            headers={'X-Hands-API-Key': HANDS_API_KEY},
            timeout=10
        )
        log(f"   Completion response: HTTP {response.status_code}")
    except Exception as e:
        log(f"⚠️ Job completion failed: {str(e)}")

def execute_follow_job(job):
    """Execute follow job"""
    job_id = job['id']
    target_username = job['target_username']
    tier = job['tier']
    accounts = job['payload']['accounts']
    
    log(f"📋 Job #{job_id}: Follow {target_username} ({tier})")
    log(f"💪 Workforce: {len(accounts)} accounts")
    
    results = {
        'total': len(accounts),
        'success': 0,
        'failed': 0,
        'already_followed': 0,
        'errors': []
    }
    
    session = Session()
    
    try:
        # Check target exists
        from instagrapi.exceptions import UserNotFound, PrivateError
        from instagrapi import Client
        
        target_user_id = None
        try:
            temp_client = ig_automation._create_client()
            if accounts:
                session_file = os.path.join('sessions', f"{accounts[0]['username']}.json")
                if os.path.exists(session_file):
                    temp_client.load_settings(session_file)
                    temp_client.login(accounts[0]['username'], accounts[0]['password'])
                else:
                    temp_client.login(accounts[0]['username'], accounts[0]['password'])
                
                target_user = temp_client.user_info_by_username(target_username)
                target_user_id = target_user.pk
                log(f"✓ Target verified: @{target_username}")
        except UserNotFound:
            error_msg = f"Target account @{target_username} not found"
            log(f"✗ {error_msg}")
            complete_job(job_id, 'failed', error=error_msg)
            return
        except Exception as e:
            log(f"⚠️ Target verification error: {str(e)}")
        
        # Execute follows
        for i, account_data in enumerate(accounts):
            progress = i + 1
            username = account_data['username']
            password = account_data['password']
            account_id = account_data['id']
            
            send_progress(job_id, progress, len(accounts), f'Workforce: @{username} following @{target_username}...')
            
            client = ig_automation._create_client()
            session_file = os.path.join('sessions', f"{username}.json")
            
            try:
                # Login
                if os.path.exists(session_file):
                    client.load_settings(session_file)
                    try:
                        client.login(username, password)
                    except:
                        client.login(username, password)
                else:
                    client.login(username, password)
                    client.dump_settings(session_file)
                
                # Follow
                log(f"[{progress}/{len(accounts)}] 👥 @{username} → @{target_username}...")
                if target_user_id:
                    client.user_follow(target_user_id)
                else:
                    target_user = client.user_info_by_username(target_username)
                    client.user_follow(target_user.pk)
                
                log(f"✓ Successfully followed")
                results['success'] += 1
                
                # Log action
                action_log = ActionLog(
                    donor_account=username,
                    target=target_username,
                    tier=tier,
                    result='success'
                )
                session.add(action_log)
                
                # Mark account as used
                account = session.query(DonatedAccount).filter_by(id=account_id).first()
                if account:
                    account.status = 'used'
                    account.tier_used = tier
                    account.used_at = datetime.utcnow()
                
                session.commit()
                
            except Exception as e:
                error_msg = str(e)
                log(f"✗ Follow failed: {error_msg}")
                results['failed'] += 1
                results['errors'].append(f"@{username}: {error_msg}")
                
                # Log failed action
                action_log = ActionLog(
                    donor_account=username,
                    target=target_username,
                    tier=tier,
                    result='failed'
                )
                action_log.error = error_msg  # Set error field separately
                session.add(action_log)
                session.commit()
            
            # Rate limiting
            time.sleep(1)
        
        # Complete job
        log(f"✓ Job #{job_id} complete: {results['success']} success, {results['failed']} failed")
        complete_job(job_id, 'complete', result=results)
        
    except Exception as e:
        log(f"✗ Job #{job_id} failed: {str(e)}")
        complete_job(job_id, 'failed', error=str(e))
    finally:
        session.close()

def execute_verify_job(job):
    """Execute account verification job"""
    job_id = job['id']
    username = job['payload']['username']
    password = job['payload']['password']
    user_id = job.get('user_id')
    
    log(f"📋 Job #{job_id}: Verify @{username}")
    
    session = Session()
    
    try:
        # Verify account
        success, message = ig_automation.verify_account(username, password)
        
        if success:
            # Save account to database
            account = DonatedAccount(
                username=username,
                password=password,
                user_id=user_id
            )
            session.add(account)
            
            # Increment user's free targets
            from models import User
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.free_targets += 1
            
            session.commit()
            
            log(f"✓ Account verified and saved")
            complete_job(job_id, 'complete', result={'username': username, 'verified': True})
        else:
            log(f"✗ Verification failed: {message}")
            complete_job(job_id, 'failed', error=message)
    
    except Exception as e:
        log(f"✗ Job #{job_id} failed: {str(e)}")
        complete_job(job_id, 'failed', error=str(e))
    finally:
        session.close()

def execute_profile_lookup_job(job):
    """Execute profile lookup job"""
    job_id = job['id']
    username = job['payload']['username']
    
    log(f"📋 Job #{job_id}: Lookup @{username}")
    
    try:
        profile_info = ig_automation.get_profile_info(username)
        
        if profile_info:
            log(f"✓ Profile fetched: @{username}")
            complete_job(job_id, 'complete', result=profile_info)
        else:
            log(f"✗ Profile not found")
            complete_job(job_id, 'failed', error='Profile not found')
    
    except Exception as e:
        log(f"✗ Job #{job_id} failed: {str(e)}")
        complete_job(job_id, 'failed', error=str(e))

def process_job(job):
    """Process a job based on its type"""
    job_type = job['job_type']
    
    log(f"⚙️ Processing job #{job['id']} ({job_type})")
    
    if job_type == 'follow':
        execute_follow_job(job)
    elif job_type == 'verify':
        execute_verify_job(job)
    elif job_type == 'profile_lookup':
        execute_profile_lookup_job(job)
    else:
        log(f"⚠️ Unknown job type: {job_type}")
        complete_job(job['id'], 'failed', error=f"Unknown job type: {job_type}")

def main():
    """Main worker loop - run for a limited time for testing"""
    log("=" * 60)
    log("🚀 Hands Worker Test Starting")
    log(f"🧠 Brain URL: {BRAIN_URL}")
    log(f"📊 Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite'}")
    log(f"📸 System Account: @{SYSTEM_IG_USERNAME}")
    log(f"⏱️  Poll Interval: {POLL_INTERVAL}s")
    log("=" * 60)
    
    # Run for a limited number of cycles for testing
    max_cycles = 3
    cycle_count = 0
    
    while cycle_count < max_cycles:
        try:
            cycle_count += 1
            log(f"🔄 Polling cycle {cycle_count}/{max_cycles}")
            
            # Poll for job
            job = poll_for_job()
            
            if job:
                log(f"🎯 Job received: #{job['id']} ({job['job_type']})")
                process_job(job)
                log("✅ Job processing completed")
                # Break after processing one job for this test
                break
            else:
                # No jobs, wait
                log("⏳ No jobs available, waiting...")
                time.sleep(POLL_INTERVAL)
        
        except KeyboardInterrupt:
            log("⚠️ Shutting down...")
            break
        except Exception as e:
            log(f"⚠️ Worker error: {str(e)}")
            time.sleep(POLL_INTERVAL)
    
    log("👋 Hands Worker Test Complete")

if __name__ == '__main__':
    main()