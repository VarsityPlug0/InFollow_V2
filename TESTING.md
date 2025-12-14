# Test Script for Instagram Barter System

## Manual Testing Guide

### 1. Test User Interface
- [ ] Open http://localhost:5000
- [ ] Verify stats display (Free Test Status, Free Targets, Available Accounts)
- [ ] Check both lanes are visible (Free Test Lane & Donation Reward Lane)

### 2. Test Donation Flow
**Prerequisites:** You need a real Instagram test account

Steps:
1. Navigate to "Donate Instagram Account" section
2. Enter Instagram username and password
3. Click "Donate Account"
4. Expected Results:
   - Account should be verified via Instagram login
   - Success message: "Account @username donated successfully! You now have 1 free target(s)."
   - Free Targets counter should increment by 1
   - Available Accounts counter should increment by 1

### 3. Test Free Test Lane
**Prerequisites:** At least 20 donated accounts in the system

Steps:
1. Navigate to "Free Test Lane"
2. Enter a target Instagram username
3. Click "Try Free (20 Followers)"
4. Expected Results:
   - Progress bar shows live updates (e.g., "7/20")
   - Each follow action is logged
   - Final results show: Success, Already Following, Failed counts
   - Button changes to "Free Test Used" and is disabled
   - Target is permanently burned (cannot be reused)

### 4. Test Donation Reward Lane
**Prerequisites:** At least 1 free target available (from donation), 30 donated accounts

Steps:
1. Navigate to "Donation Reward Lane"
2. Enter a different target Instagram username
3. Click "Boost Target (30 Followers)"
4. Expected Results:
   - Progress bar shows live updates (e.g., "15/30")
   - Each follow action is logged
   - Final results show: Success, Already Following, Failed counts
   - Free Targets counter decrements by 1
   - Target is permanently burned

### 5. Test Target Reuse Prevention
Steps:
1. Try to use the same target from Free Test in Donation Lane
2. Expected Result: Error "Target @username has already been used in free_test lane"
3. Try to use the same target from Donation Lane again
4. Expected Result: Error "Target @username has already been used in donation lane"

### 6. Test Admin Dashboard
Steps:
1. Navigate to http://localhost:5000/admin
2. Enter admin password (default: "admin123")
3. Click "Login"
4. Expected Results:
   - Dashboard shows all stats
   - View donated accounts with status (unused/used)
   - View targets with tier (free_test/donation)
   - View action logs with results
   - Can remove bad accounts

### 7. Test Edge Cases

#### No Donated Accounts
- Try Free Test with 0 accounts: Should show error "Not enough donated accounts"
- Try Donation Boost with 0 accounts: Should show error "Not enough donated accounts"

#### No Free Targets
- Try Donation Boost with 0 free targets: Button should be disabled
- Message: "Donate to Unlock"

#### Invalid Instagram Account
- Donate with fake credentials: Should show error "Invalid password" or "Login failed"

#### Duplicate Donation
- Try to donate the same account twice: Should show error "This account has already been donated"

#### Invalid Target
- Use non-existent Instagram username: Should show error "Target account @username not found"

## Automated Testing (Future)

For production deployment, consider:
- Unit tests for models and routes
- Integration tests for Instagram API
- Mock testing for instagrapi functions
- Load testing for concurrent users

## Known Limitations

1. **Instagram Rate Limits**: Too many follow actions may trigger rate limits
2. **2FA Accounts**: Accounts with 2FA will fail verification
3. **Private Accounts**: Can still be followed, but may require manual approval
4. **Session Persistence**: Sessions stored locally in `sessions/` folder

## Security Notes

- Change `ADMIN_PASSWORD` in production
- Set strong `SECRET_KEY` for sessions
- Never expose admin dashboard publicly
- Store passwords encrypted in production (current implementation stores plain text)
