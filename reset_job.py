from app import app, db
from models import Job

def reset_job():
    with app.app_context():
        job = Job.query.get(1)
        if job:
            print(f"Resetting job #{job.id} from '{job.status}' to 'pending'")
            job.status = 'pending'
            job.started_at = None
            job.completed_at = None
            job.error = None
            job.result = None
            db.session.commit()
            print("Job reset successfully")
        else:
            print("Job not found")

if __name__ == '__main__':
    reset_job()