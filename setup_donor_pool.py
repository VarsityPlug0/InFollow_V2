"""
Setup Donor Pool - Ensure virg.ildebie is in the donor pool
"""

from models import db, DonatedAccount, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Connect to database
engine = create_engine('sqlite:///barter.db')
Session = sessionmaker(bind=engine)
session = Session()

print("=" * 70)
print("🔧 DONOR POOL SETUP")
print("=" * 70)
print()

# Check current donor accounts
print("Step 1: Checking current donor pool...")
accounts = session.query(DonatedAccount).all()
print(f"Total donor accounts in database: {len(accounts)}")
print()

if accounts:
    print("Current accounts:")
    for acc in accounts:
        print(f"  - @{acc.username}")
        print(f"    Status: {acc.status}")
        print(f"    Tier: {acc.tier_used or 'None'}")
        print(f"    User ID: {acc.user_id or 'None (Admin)'}")
        print()
else:
    print("⚠️  No donor accounts found!")
    print()

# Check for virg.ildebie
print("Step 2: Checking for virg.ildebie account...")
virg_account = session.query(DonatedAccount).filter_by(username='virg.ildebie').first()

if virg_account:
    print(f"✅ Account found: @{virg_account.username}")
    print(f"   Status: {virg_account.status}")
    print(f"   Tier: {virg_account.tier_used or 'None'}")
    print()
    
    # Reset to unused if it's been used
    if virg_account.status != 'unused':
        print("🔄 Resetting account to 'unused' status...")
        virg_account.status = 'unused'
        virg_account.tier_used = None
        virg_account.used_at = None
        session.commit()
        print("✅ Account reset to unused!")
    else:
        print("✅ Account already unused and ready!")
else:
    print("⚠️  Account NOT found! Adding now...")
    print()
    
    # Add the account
    new_account = DonatedAccount(
        username='virg.ildebie',
        password='ShadowTest31@',
        status='unused',
        tier_used=None,
        user_id=None,  # Admin-donated (no user_id)
        donated_at=datetime.utcnow(),
        used_at=None
    )
    
    session.add(new_account)
    session.commit()
    
    print("✅ Account added successfully!")
    print(f"   Username: @{new_account.username}")
    print(f"   Status: {new_account.status}")
    print(f"   User ID: None (Admin)")

print()
print("Step 3: Verifying pool status...")
unused_count = session.query(DonatedAccount).filter_by(status='unused').count()
used_count = session.query(DonatedAccount).filter_by(status='used').count()

print(f"📊 Pool Status:")
print(f"   Unused accounts: {unused_count}")
print(f"   Used accounts: {used_count}")
print(f"   Total accounts: {unused_count + used_count}")
print()

if unused_count > 0:
    print("✅ SUCCESS! Free Test Lane is ready to work!")
    print(f"   {unused_count} account(s) available for testing")
    print()
    print("📋 Unused Accounts:")
    unused_accounts = session.query(DonatedAccount).filter_by(status='unused').all()
    for acc in unused_accounts:
        print(f"   - @{acc.username}")
else:
    print("❌ WARNING! No unused accounts available")
    print("   Free Test Lane will show 'No donor accounts available' error")

print()
print("=" * 70)
print("✅ SETUP COMPLETE!")
print("=" * 70)
print()
print("💡 Next Steps:")
print("   1. Start Brain: python app.py")
print("   2. Visit: http://localhost:5000")
print("   3. Click 'Claim FREE Followers'")
print("   4. Watch it work with @virg.ildebie account!")
print()

session.close()
