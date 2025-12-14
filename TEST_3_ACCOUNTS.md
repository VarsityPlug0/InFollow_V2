# 🧪 3-Account Growth Test Guide

## 🎯 Objective
Test the system with 3 Instagram accounts to verify the donation → credit → boost cycle works correctly, even starting with just 1 account.

---

## 📋 Pre-Test Setup

### Step 1: Reset Database (Fresh Start)
```bash
python reset_test.py
```
Type `yes` when prompted to clear all data.

### Step 2: Start Server (if not running)
```bash
python app.py
```
Server should run on http://localhost:5000

### Step 3: Start Live Monitor (Optional but Recommended)
Open a **second terminal** and run:
```bash
python monitor_db.py
```
This shows real-time database updates as you test!

---

## 🧪 Test Execution

### 📧 Phase 0: Sign Up
1. Visit http://localhost:5000
2. Enter a target username (e.g., `testuser123`)
3. Sign up with email: `test@example.com`
4. **Expected:** You'll see the free test option

### 🎁 Cycle 1: First Account
1. **Donate Account 1**
   - Go to `/donate`
   - Enter credentials (use real test account)
   - Submit donation
   
2. **Expected Results:**
   - ✅ "Account verified and added!"
   - ✅ "+1 credit earned"
   - ✅ Dashboard shows: "💎 1 Credit (30 followers)"

3. **Use Credit 1**
   - Enter target username
   - Click "Use 1 Credit (30 Followers)"
   - Watch real-time progress
   
4. **Expected Results:**
   - ✅ System uses Account 1 to follow target
   - ✅ "1 follower delivered" (proportional delivery)
   - ✅ Account 1 marked as "used"
   - ✅ Dashboard shows: "0 credits remaining"

### 🎁 Cycle 2: Second Account
1. **Donate Account 2**
   - Return to `/donate`
   - Enter second account credentials
   - Submit donation
   
2. **Expected Results:**
   - ✅ "+1 credit earned"
   - ✅ Dashboard shows: "💎 1 Credit (30 followers)"

3. **Use Credit 2**
   - Enter NEW target username (different from first)
   - Click "Use 1 Credit (30 Followers)"
   
4. **Expected Results:**
   - ✅ Account 2 follows new target
   - ✅ "1 follower delivered"
   - ✅ Credits back to 0

### 🎁 Cycle 3: Third Account
1. **Donate Account 3**
   - Return to `/donate`
   - Enter third account credentials
   
2. **Use Credit 3**
   - Enter ANOTHER new target
   - Use the credit
   
3. **Expected Results:**
   - ✅ Account 3 follows target
   - ✅ "1 follower delivered"

---

## ✅ Success Criteria

### Database State After All Cycles:
```
👥 Users: 1
💼 Donated Accounts: 3 (all used)
🎯 Targets: 3
📝 Action Logs: 3
```

### User State:
- Free Test: Not used (we only used credits)
- Credits: 0 (all spent)
- Donated Accounts: 3

### Key Behaviors to Verify:
1. ✅ System works with 1 account at a time (proportional delivery)
2. ✅ Each donation gives exactly 1 credit
3. ✅ Each credit delivers followers (1 per account available)
4. ✅ Accounts are marked "used" after delivery
5. ✅ Targets cannot be reused
6. ✅ Credits decrement correctly
7. ✅ Dashboard shows accurate stats
8. ✅ Auto-redirect works after delivery

---

## 🔍 Monitoring Commands

### Check Database Anytime:
```bash
python check_db.py
```

### Watch Live Updates:
```bash
python monitor_db.py
```

### Check Server Logs:
Watch the terminal where `python app.py` is running for:
- `[DONATE]` - Donation events
- `[CREDIT]` - Credit usage
- `[WEBSOCKET]` - Real-time follow execution
- `[INSTAGRAPI]` - Instagram API calls

---

## 🐛 Expected Behaviors

### Proportional Delivery:
- With 1 account → Delivers 1 follower (not 30)
- With 2 accounts → Delivers 2 followers (not 30)
- With 30+ accounts → Delivers 30 followers

### Burn-Once:
- Each account used only once
- Each target used only once
- No reuse allowed

### Credits:
- 1 donation = 1 credit
- 1 credit = attempt to deliver 30 followers (proportional to pool)
- Credits don't stack beyond donations

---

## 📊 What to Observe

### In Browser:
- Smooth donation flow
- Clear credit display
- Real-time progress bars
- Success messages
- Auto-redirect to dashboard

### In Monitor:
- Accounts appearing as "unused"
- Accounts changing to "used" after boost
- Targets being created
- Action logs accumulating
- User credits incrementing/decrementing

### In Server Logs:
- Instagram login attempts
- Follow actions executing
- Database updates
- Socket.IO events

---

## 🎯 Growth Pattern Expected

```
Start:     0 accounts, 0 credits
Donate 1:  1 account,  1 credit
Use 1:     1 used,     0 credits → 1 follower delivered
Donate 2:  2 accounts, 1 credit  (1 used, 1 unused)
Use 2:     2 used,     0 credits → 1 follower delivered
Donate 3:  3 accounts, 1 credit  (2 used, 1 unused)
Use 3:     3 used,     0 credits → 1 follower delivered

Total: 3 followers delivered across 3 targets
```

---

## 🚀 Ready to Test!

1. ✅ Run `python reset_test.py` (type `yes`)
2. ✅ Start server: `python app.py`
3. ✅ (Optional) Start monitor in second terminal: `python monitor_db.py`
4. ✅ Open browser: http://localhost:5000
5. ✅ Follow the test cycles above
6. ✅ Observe real-time updates
7. ✅ Verify all success criteria

**Good luck with the test!** 🎉
