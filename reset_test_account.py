#!/usr/bin/env python3
"""Reset test account to unused status"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, '.')
from models import DonatedAccount
from datetime import datetime

engine = create_engine('sqlite:///barter.db')
Session = sessionmaker(bind=engine)
db_session = Session()

print("Resetting test account to unused status...")

# Find the test account
test_account = db_session.query(DonatedAccount).filter_by(username="bevanmakaveli").first()

if not test_account:
    print("❌ Test account not found!")
    db_session.close()
    sys.exit(1)

print(f"Found account: @{test_account.username}")
print(f"Current status: {test_account.status}")

# Reset to unused
test_account.status = "unused"
test_account.tier_used = None
test_account.used_at = None

db_session.commit()

print(f"✅ Reset account to: {test_account.status}")

# Verify
count = db_session.query(DonatedAccount).filter_by(status='unused').count()
print(f"\n📊 Total unused accounts: {count}")

db_session.close()