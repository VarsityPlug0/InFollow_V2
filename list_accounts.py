#!/usr/bin/env python3
"""List all accounts in database"""

from app import app
from models import DonatedAccount

def list_accounts():
    with app.app_context():
        accounts = DonatedAccount.query.all()
        print("Accounts in database:")
        for account in accounts:
            print(f"  @{account.username} - {account.status}")

if __name__ == '__main__':
    list_accounts()