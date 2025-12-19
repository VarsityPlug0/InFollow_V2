#!/usr/bin/env python3
"""Reset stuck job to pending state"""

from app import app, db
from models import Job

def reset_stuck_job():
    with app.app_context():
        # Find jobs that are stuck in processing state
        stuck_jobs = Job.query.filter_by(status='processing').all()
        
        if not stuck_jobs:
            print("No stuck jobs found")
            return
        
        for job in stuck_jobs:
            print(f"Resetting job #{job.id} from '{job.status}' to 'pending'")
            job.status = 'pending'
            job.started_at = None
            
        db.session.commit()
        print(f"Reset {len(stuck_jobs)} stuck job(s)")

if __name__ == '__main__':
    reset_stuck_job()