#!/usr/bin/env python3
"""
Reset database for clean 3-account test
This will clear all data and prepare for a fresh test cycle
"""

from app import app, db
from models import DonatedAccount, Target, User, ActionLog

def reset_for_test():
    with app.app_context():
        print("\n" + "="*60)
        print("🧹 CLEANING DATABASE FOR FRESH TEST")
        print("="*60)
        
        # Count before
        print(f"\n📊 Before cleanup:")
        print(f"  Users: {User.query.count()}")
        print(f"  Donated Accounts: {DonatedAccount.query.count()}")
        print(f"  Targets: {Target.query.count()}")
        print(f"  Action Logs: {ActionLog.query.count()}")
        
        # Clear all data
        print(f"\n🗑️  Deleting all records...")
        ActionLog.query.delete()
        Target.query.delete()
        DonatedAccount.query.delete()
        User.query.delete()
        db.session.commit()
        
        print(f"✅ Database cleared!")
        
        # Verify
        print(f"\n📊 After cleanup:")
        print(f"  Users: {User.query.count()}")
        print(f"  Donated Accounts: {DonatedAccount.query.count()}")
        print(f"  Targets: {Target.query.count()}")
        print(f"  Action Logs: {ActionLog.query.count()}")
        
        print("\n" + "="*60)
        print("✨ READY FOR 3-ACCOUNT GROWTH TEST!")
        print("="*60)
        print("\n📋 Test Plan:")
        print("  1. Visit http://localhost:5000")
        print("  2. Sign up with test email")
        print("  3. Donate Account 1 → Get 1 credit")
        print("  4. Use credit → Boost target (1 follower)")
        print("  5. Donate Account 2 → Get 1 credit")
        print("  6. Use credit → Boost target (1 follower)")
        print("  7. Donate Account 3 → Get 1 credit")
        print("  8. Use credit → Boost target (1 follower)")
        print("\n💡 System should handle 1 account at a time gracefully!")
        print("="*60 + "\n")

if __name__ == '__main__':
    confirm = input("⚠️  This will DELETE ALL DATA. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_for_test()
    else:
        print("❌ Cancelled.")
