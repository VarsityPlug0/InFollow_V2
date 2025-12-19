from app import app
from models import Job, DonatedAccount

def check_db():
    with app.app_context():
        jobs = Job.query.count()
        accounts = DonatedAccount.query.count()
        unused = DonatedAccount.query.filter_by(status='unused').count()
        
        print(f"Jobs: {jobs}")
        print(f"Accounts: {accounts}")
        print(f"Unused accounts: {unused}")
        
        if jobs > 0:
            print("\nJob details:")
            for job in Job.query.all():
                print(f"  Job #{job.id}: {job.job_type} - {job.status}")
        
        if accounts > 0:
            print("\nAccount details:")
            for account in DonatedAccount.query.all():
                print(f"  @{account.username}: {account.status}")

if __name__ == '__main__':
    check_db()