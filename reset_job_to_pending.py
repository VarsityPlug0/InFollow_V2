#!/usr/bin/env python3
"""Reset specific job to pending status"""

from app import app, db
from models import Job

def reset_job_to_pending(job_id):
    with app.app_context():
        # Find the job
        job = Job.query.get(job_id)
        
        if not job:
            print(f"❌ Job #{job_id} not found!")
            return False
        
        print(f"Found job #{job.id}")
        print(f"Current status: {job.status}")
        
        # Reset to pending
        job.status = "pending"
        job.started_at = None
        job.completed_at = None
        job.error = None
        job.result = None
        
        db.session.commit()
        
        print(f"✅ Reset job to: {job.status}")
        return True

if __name__ == '__main__':
    reset_job_to_pending(1)