import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///barter.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_FOLDER = 'sessions'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
