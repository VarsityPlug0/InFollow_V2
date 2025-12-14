"""Remove system validation account from donated accounts pool"""
from app import app, db
from models import DonatedAccount

def cleanup():
    with app.app_context():
        # Remove virg.ildebie from donated accounts (it's for system validation only)
        account = DonatedAccount.query.filter_by(username='virg.ildebie').first()
        if account:
            db.session.delete(account)
            db.session.commit()
            print("✓ Removed virg.ildebie from donated accounts pool")
            print("  (This account is reserved for system profile lookups only)")
        else:
            print("✓ virg.ildebie is not in donated accounts pool")
        
        # Show remaining donated accounts
        remaining = DonatedAccount.query.all()
        print(f"\nRemaining donated accounts: {len(remaining)}")
        for acc in remaining:
            print(f"  - @{acc.username} (status: {acc.status}, user_id: {acc.user_id})")

if __name__ == '__main__':
    cleanup()
