import os
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, BadPassword, UserNotFound, PrivateError
from datetime import datetime
from models import db, DonatedAccount, Target, ActionLog

class InstagramAutomation:
    def __init__(self, session_folder='sessions'):
        self.session_folder = session_folder
        if not os.path.exists(session_folder):
            os.makedirs(session_folder)
    
    def get_profile_info(self, username):
        """Fetch Instagram profile info using system validation account"""
        print(f"[INSTAGRAPI] Fetching profile for @{username}...")
        
        # Use dedicated system validation account for profile lookups
        # This account is NOT in the donated pool - it's reserved for validation only
        SYSTEM_USERNAME = 'virg.ildebie'
        SYSTEM_PASSWORD = 'ShadowTest31@'
        
        client = Client()
        session_file = os.path.join(self.session_folder, f"{SYSTEM_USERNAME}.json")
        
        try:
            # Login with system validation account
            if os.path.exists(session_file):
                client.load_settings(session_file)
                try:
                    client.login(SYSTEM_USERNAME, SYSTEM_PASSWORD)
                except:
                    client.login(SYSTEM_USERNAME, SYSTEM_PASSWORD)
            else:
                client.login(SYSTEM_USERNAME, SYSTEM_PASSWORD)
                client.dump_settings(session_file)
            
            # Fetch target profile
            user_info = client.user_info_by_username(username)
            
            profile_data = {
                'username': user_info.username,
                'full_name': user_info.full_name,
                'follower_count': user_info.follower_count,
                'is_private': user_info.is_private,
                'profile_pic_url': str(user_info.profile_pic_url) if user_info.profile_pic_url else None,
                'biography': user_info.biography or ''
            }
            
            print(f"[INSTAGRAPI] ✓ Profile fetched: @{username} ({profile_data['follower_count']} followers)")
            return profile_data
            
        except UserNotFound:
            print(f"[INSTAGRAPI] ✗ User @{username} not found")
            return None
        except Exception as e:
            print(f"[INSTAGRAPI] ✗ Error fetching profile: {str(e)}")
            return None
    
    def verify_account(self, username, password):
        """Verify donated account can login"""
        print(f"\n[INSTAGRAPI] Verifying account: @{username}")
        client = Client()
        session_file = os.path.join(self.session_folder, f"{username}.json")
        
        try:
            # Try to login
            print(f"[INSTAGRAPI] Attempting login for @{username}...")
            client.login(username, password)
            print(f"[INSTAGRAPI] ✓ Login successful for @{username}")
            
            # Save session
            client.dump_settings(session_file)
            print(f"[INSTAGRAPI] ✓ Session saved to {session_file}")
            
            return True, "Account verified successfully"
        
        except BadPassword:
            print(f"[INSTAGRAPI] ✗ Bad password for @{username}")
            return False, "Invalid password"
        except ChallengeRequired:
            print(f"[INSTAGRAPI] ✗ Challenge required for @{username}")
            return False, "Account requires verification (challenge)"
        except Exception as e:
            print(f"[INSTAGRAPI] ✗ Login failed for @{username}: {str(e)}")
            return False, f"Login failed: {str(e)}"
    
    def execute_follows(self, target_username, tier, count, socketio=None):
        """Execute follow actions using ALL available donated accounts (workforce model)"""
        print(f"\n[INSTAGRAPI] Starting follow execution:")
        print(f"[INSTAGRAPI] Target: @{target_username}")
        print(f"[INSTAGRAPI] Tier: {tier}")
        print(f"[INSTAGRAPI] Requested count: {count}")
        
        # WORKFORCE MODEL: Use ALL unused accounts in the pool
        # Every donation strengthens the workforce, and the entire workforce works together
        all_accounts = DonatedAccount.query.filter_by(status='unused').all()
        
        print(f"[INSTAGRAPI] 💪 Workforce size: {len(all_accounts)} accounts ready")
        
        if len(all_accounts) == 0:
            error_msg = "No donated accounts available in the workforce. System needs donations to operate."
            print(f"[INSTAGRAPI] ✗ {error_msg}")
            return False, error_msg
        
        # Use ALL available accounts (workforce grows with each donation)
        accounts = all_accounts
        actual_count = len(accounts)
        
        print(f"[INSTAGRAPI] 🚀 Using entire workforce: {actual_count} accounts will follow @{target_username}")
        
        results = {
            'total': actual_count,
            'success': 0,
            'failed': 0,
            'already_followed': 0,
            'errors': []
        }
        
        # Check if target exists
        target_user_id = None
        try:
            temp_client = Client()
            if accounts:
                session_file = os.path.join(self.session_folder, f"{accounts[0].username}.json")
                if os.path.exists(session_file):
                    temp_client.load_settings(session_file)
                    temp_client.login(accounts[0].username, accounts[0].password)
                else:
                    temp_client.login(accounts[0].username, accounts[0].password)
                
                target_user = temp_client.user_info_by_username(target_username)
                target_user_id = target_user.pk
        except UserNotFound:
            return False, f"Target account @{target_username} not found"
        except PrivateError:
            # Private accounts can still be followed, continue
            pass
        except Exception as e:
            return False, f"Could not verify target account: {str(e)}"
        
        # Execute follows with entire workforce
        for i, account in enumerate(accounts):
            progress = i + 1
            
            if socketio:
                socketio.emit('progress', {
                    'current': progress,
                    'total': actual_count,
                    'status': f'Workforce member @{account.username} following @{target_username}...'
                })
            
            client = Client()
            session_file = os.path.join(self.session_folder, f"{account.username}.json")
            
            try:
                # Load session or login
                if os.path.exists(session_file):
                    client.load_settings(session_file)
                    try:
                        client.login(account.username, account.password)
                    except:
                        client.login(account.username, account.password)
                else:
                    client.login(account.username, account.password)
                    client.dump_settings(session_file)
                
                # Attempt to follow
                print(f"[INSTAGRAPI] [{progress}/{actual_count}] 👥 Workforce: @{account.username} → @{target_username}...")
                if target_user_id:
                    client.user_follow(target_user_id)
                else:
                    # Fallback if we couldn't get user_id earlier
                    target_user = client.user_info_by_username(target_username)
                    client.user_follow(target_user.pk)
                
                print(f"[INSTAGRAPI] ✓ Successfully followed")
                # Mark as success
                results['success'] += 1
                
                # Log action
                log = ActionLog(
                    donor_account=account.username,
                    target=target_username,
                    tier=tier,
                    result='success'
                )
                db.session.add(log)
                
                # Mark account as used
                account.status = 'used'
                account.tier_used = tier
                account.used_at = datetime.utcnow()
                
                db.session.commit()
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                error_msg = str(e)
                print(f"[INSTAGRAPI] ✗ Error with @{account.username}: {error_msg}")
                
                # Check if already following
                if 'already' in error_msg.lower() or 'following' in error_msg.lower():
                    results['already_followed'] += 1
                    result_type = 'already_followed'
                    print(f"[INSTAGRAPI] (Already following)")
                else:
                    results['failed'] += 1
                    result_type = 'error'
                    results['errors'].append(f"@{account.username}: {error_msg}")
                
                # Log action
                log = ActionLog(
                    donor_account=account.username,
                    target=target_username,
                    tier=tier,
                    result=result_type,
                    error=error_msg
                )
                db.session.add(log)
                
                # Still mark account as used
                account.status = 'used'
                account.tier_used = tier
                account.used_at = datetime.utcnow()
                
                db.session.commit()
                
                time.sleep(1)
        
        print(f"\n[INSTAGRAPI] Follow execution complete:")
        print(f"[INSTAGRAPI] Success: {results['success']}")
        print(f"[INSTAGRAPI] Already Following: {results['already_followed']}")
        print(f"[INSTAGRAPI] Failed: {results['failed']}")
        
        return True, results
