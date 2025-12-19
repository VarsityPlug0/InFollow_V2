#!/usr/bin/env python3
"""Check account status"""

from app import app
from models import DonatedAccount

def check_accounts():
    with app.app_context():
        total = DonatedAccount.query.count()
        unused = DonatedAccount.query.filter_by(status='unused').count()
        used = DonatedAccount.query.filter_by(status='used').count()
        
        print(f"Total accounts: {total}")
        print(f"Unused accounts: {unused}")
        print(f"Used accounts: {used}")
        
        if total > 0:
            print("\nAccount details:")
            for account in DonatedAccount.query.all():
                print(f"  @{account.username} - {account.status}")

if __name__ == '__main__':
    check_accounts()