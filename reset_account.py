#!/usr/bin/env python3
"""Reset specific account to unused status"""

from app import app, db
from models import DonatedAccount

def reset_account(username):
    with app.app_context():
        # Find the account
        account = DonatedAccount.query.filter_by(username=username).first()
        
        if not account:
            print(f"❌ Account @{username} not found!")
            return False
        
        print(f"Found account: @{account.username}")
        print(f"Current status: {account.status}")
        
        # Reset to unused
        account.status = "unused"
        account.tier_used = None
        account.used_at = None
        
        db.session.commit()
        
        print(f"✅ Reset account to: {account.status}")
        return True

if __name__ == '__main__':
    reset_account("bevanmakaveli")