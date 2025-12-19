from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # For authenticated users
    is_authenticated = db.Column(db.Boolean, default=False, nullable=False)
    free_test_used = db.Column(db.Boolean, default=False, nullable=False)
    free_targets = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email or self.session_id}>'

class DonatedAccount(db.Model):
    __tablename__ = 'donated_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='unused', nullable=False)  # unused, used
    tier_used = db.Column(db.String(20))  # free_test, donation
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Track who donated
    donated_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('donated_accounts', lazy=True))
    
    def __repr__(self):
        return f'<DonatedAccount {self.username} - {self.status}>'

class Target(db.Model):
    __tablename__ = 'targets'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    tier = db.Column(db.String(20), nullable=False)  # free_test, donation
    burned = db.Column(db.Boolean, default=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('targets', lazy=True))
    
    def __repr__(self):
        return f'<Target {self.username} - {self.tier}>'

class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_account = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100), nullable=False)
    tier = db.Column(db.String(20), nullable=False)  # free_test, donation
    result = db.Column(db.String(20), nullable=False)  # success, failed, already_followed, error
    error = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ActionLog {self.donor_account} -> {self.target} [{self.result}]>'

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(50), nullable=False)  # 'follow', 'verify', 'profile_lookup'
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processing, complete, failed
    target_username = db.Column(db.String(100))
    tier = db.Column(db.String(20))  # free_test, donation
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    payload = db.Column(db.JSON)  # Additional job data (accounts, passwords, etc.)
    result = db.Column(db.JSON)  # Job results
    retry_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error = db.Column(db.Text)
    
    user = db.relationship('User', backref=db.backref('jobs', lazy=True))
    
    def __repr__(self):
        return f'<Job {self.id} - {self.job_type} [{self.status}]>'
