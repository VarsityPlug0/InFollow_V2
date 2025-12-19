#!/usr/bin/env python3
"""Check current jobs in database"""

from app import app, db
from models import Job

def check_jobs():
    with app.app_context():
        print("\n" + "="*50)
        print("📋 CURRENT JOBS")
        print("="*50)
        
        jobs = Job.query.all()
        
        if not jobs:
            print("No jobs found in database")
            return
        
        for job in jobs:
            print(f"\nJob #{job.id}")
            print(f"  Type: {job.job_type}")
            print(f"  Status: {job.status}")
            print(f"  Target: @{job.target_username or 'N/A'}")
            print(f"  Tier: {job.tier or 'N/A'}")
            print(f"  Created: {job.created_at}")
            print(f"  Started: {job.started_at or 'Not started'}")
            print(f"  Completed: {job.completed_at or 'Not completed'}")
            if job.error:
                print(f"  Error: {job.error}")

if __name__ == '__main__':
    check_jobs()