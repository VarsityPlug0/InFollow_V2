from app import app
from models import Job

with app.app_context():
    job = Job.query.get(4)
    if job:
        print(f"Found job #{job.id}")
        print(f"Current status: {job.status}")
        job.status = 'pending'
        app.db.session.commit()
        print("✅ Reset job to: pending")
    else:
        print("Job not found")