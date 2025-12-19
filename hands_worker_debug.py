"""
Debug script to test Hands worker communication with Brain
"""

import os
import requests
import time
from datetime import datetime

# Configuration from environment variables
BRAIN_URL = os.environ.get('BRAIN_URL', 'http://localhost:5000')
HANDS_API_KEY = os.environ.get('HANDS_API_KEY', 'dev-hands-key-change-in-production')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '5'))

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
            log(f"   Job received: {job_data}")
            return job_data
        else:
            log(f"⚠️ Poll failed: HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        log(f"⚠️ Poll error: {str(e)}")
        return None

def main():
    """Debug polling"""
    log("=" * 60)
    log("🔍 Hands Worker DEBUG")
    log(f"🧠 Brain URL: {BRAIN_URL}")
    log(f"🔑 API Key: {HANDS_API_KEY[:5]}...")
    log("=" * 60)
    
    # Test single poll
    job = poll_for_job()
    
    if job:
        log(f"✅ SUCCESS: Job #{job['id']} received")
    else:
        log("ℹ️  No job received (this is normal if no jobs exist)")

if __name__ == '__main__':
    main()