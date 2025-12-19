from app import app, db
from models import Job, DonatedAccount
from datetime import datetime

def create_test_job():
    with app.app_context():
        # Get the test account
        account = DonatedAccount.query.first()
        if not account:
            print("No donor account found!")
            return
        
        # Create job data
        accounts_data = [{
            'username': account.username,
            'password': account.password,
            'id': account.id
        }]
        
        # Create a new job
        job = Job(
            job_type='follow',
            target_username='instagram',
            tier='free_test',
            payload={'accounts': accounts_data},
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(job)
        db.session.commit()
        
        print(f"Created test job #{job.id}")
        print(f"Type: {job.job_type}")
        print(f"Target: @{job.target_username}")
        print(f"Tier: {job.tier}")
        print(f"Accounts: {len(accounts_data)}")

if __name__ == '__main__':
    create_test_job()