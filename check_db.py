#!/usr/bin/env python3
"""Quick database status checker"""

from app import app, db
from models import DonatedAccount, Target, User, ActionLog

def check_db():
    with app.app_context():
        print("\n" + "="*50)
        print("📊 CURRENT DATABASE STATE")
        print("="*50)
        
        users = User.query.count()
        accounts = DonatedAccount.query.count()
        unused = DonatedAccount.query.filter_by(status='unused').count()
        used = DonatedAccount.query.filter_by(status='used').count()
        targets = Target.query.count()
        logs = ActionLog.query.count()
        
        print(f"\n👥 Users: {users}")
        print(f"💼 Donated Accounts: {accounts}")
        print(f"   ✓ Unused: {unused}")
        print(f"   ✗ Used: {used}")
        print(f"🎯 Targets: {targets}")
        print(f"📝 Action Logs: {logs}")
        
        if accounts > 0:
            print("\n" + "="*50)
            print("💼 DONATED ACCOUNTS")
            print("="*50)
            for acc in DonatedAccount.query.all():
                tier = acc.tier_used or "not used"
                print(f"  @{acc.username:20} - {acc.status:8} ({tier})")
        
        if targets > 0:
            print("\n" + "="*50)
            print("🎯 TARGETS")
            print("="*50)
            for t in Target.query.all():
                print(f"  @{t.username:20} - {t.tier}")
        
        if users > 0:
            print("\n" + "="*50)
            print("👥 USERS")
            print("="*50)
            for u in User.query.all():
                print(f"  {u.email or 'No email':30} - Free Test: {u.free_test_used}, Credits: {u.free_targets}")
        
        print("\n" + "="*50)

if __name__ == '__main__':
    check_db()
