#!/usr/bin/env python3
"""
Real-time database monitor for testing
Shows live updates as you interact with the system
"""

import time
import os
from app import app, db
from models import DonatedAccount, Target, User, ActionLog

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_db():
    print("🔴 LIVE DATABASE MONITOR - Press Ctrl+C to stop\n")
    
    try:
        while True:
            with app.app_context():
                clear_screen()
                
                print("="*70)
                print("📊 LIVE DATABASE STATUS - Updates every 2 seconds")
                print("="*70)
                print(f"⏰ {time.strftime('%H:%M:%S')}")
                
                users = User.query.all()
                accounts = DonatedAccount.query.all()
                targets = Target.query.all()
                logs = ActionLog.query.all()
                
                # Summary
                print(f"\n📈 SUMMARY")
                print(f"  👥 Users: {len(users)}")
                print(f"  💼 Accounts: {len(accounts)} ({len([a for a in accounts if a.status == 'unused'])} unused)")
                print(f"  🎯 Targets: {len(targets)}")
                print(f"  📝 Actions: {len(logs)}")
                
                # Active user details
                active_users = [u for u in users if u.is_authenticated]
                if active_users:
                    print(f"\n👤 ACTIVE USERS")
                    for u in active_users:
                        print(f"  {u.email or 'Anonymous':30} | Credits: {u.free_targets} | Free Test: {'✓' if u.free_test_used else '✗'}")
                
                # Account status
                if accounts:
                    print(f"\n💼 DONATED ACCOUNTS")
                    for acc in accounts:
                        status_icon = "✓" if acc.status == "unused" else "✗"
                        tier = acc.tier_used or "ready"
                        print(f"  {status_icon} @{acc.username:20} | {acc.status:8} | {tier}")
                
                # Targets
                if targets:
                    print(f"\n🎯 TARGETS BOOSTED")
                    for t in targets:
                        print(f"  @{t.username:20} | {t.tier}")
                
                # Recent actions
                if logs:
                    print(f"\n📝 RECENT ACTIONS (Last 5)")
                    recent = sorted(logs, key=lambda x: x.timestamp, reverse=True)[:5]
                    for log in recent:
                        result_icon = "✓" if log.result == "success" else "✗"
                        print(f"  {result_icon} {log.donor_account:15} → {log.target:15} | {log.result}")
                
                print(f"\n{'='*70}")
                print("💡 Waiting for changes... (refreshing every 2 seconds)")
                
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped.")

if __name__ == '__main__':
    monitor_db()
