import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///barter.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_FOLDER = 'sessions'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    
    # Instagram Proxy Configuration
    # Set these environment variables on Render:
    # PROXY_HOST=proxy.example.com
    # PROXY_PORT=8080
    # PROXY_USERNAME=your_username
    # PROXY_PASSWORD=your_password
    PROXY_HOST = os.environ.get('PROXY_HOST')
    PROXY_PORT = os.environ.get('PROXY_PORT')
    PROXY_USERNAME = os.environ.get('PROXY_USERNAME')
    PROXY_PASSWORD = os.environ.get('PROXY_PASSWORD')
    
    @staticmethod
    def get_proxy_url():
        """Build proxy URL from environment variables"""
        if not Config.PROXY_HOST:
            return None
        
        if Config.PROXY_USERNAME and Config.PROXY_PASSWORD:
            # Authenticated proxy
            return f"http://{Config.PROXY_USERNAME}:{Config.PROXY_PASSWORD}@{Config.PROXY_HOST}:{Config.PROXY_PORT or 8080}"
        else:
            # Non-authenticated proxy
            return f"http://{Config.PROXY_HOST}:{Config.PROXY_PORT or 8080}"
