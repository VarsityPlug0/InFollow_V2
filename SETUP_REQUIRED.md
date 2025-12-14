# ⚠️ System Setup Required

## Issue Found

The simplified flow requires **at least one donated Instagram account** in the system to function because:

1. Instagram API requires **authentication** to fetch user profiles
2. The `get_profile_info()` method needs to **login with a donor account** first
3. Then it can fetch the target user's profile information

## Current Status

- **Donor Accounts**: 0
- **Status**: System cannot fetch profiles

## How to Fix

### Option 1: Add Test Donor Account (Recommended for Testing)

```bash
# Add a test Instagram account to the database
python -c "
from app import app, db
from models import DonatedAccount

app.app_context().push()

# Add your test Instagram account
donor = DonatedAccount(
    username='YOUR_INSTAGRAM_USERNAME',
    password='YOUR_INSTAGRAM_PASSWORD'
)
db.session.add(donor)
db.session.commit()

print('✓ Donor account added successfully')
"
```

### Option 2: Use Admin Dashboard

1. Access: http://localhost:5000/admin
2. Password: `admin123`
3. The old complex UI still has donation functionality
4. Temporarily switch back to add accounts

### Option 3: Add via API (if you have credentials)

```python
import requests

response = requests.post('http://localhost:5000/api/donate', json={
    'username': 'your_instagram_username',
    'password': 'your_instagram_password'
})

print(response.json())
```

## Why This Happens

Instagram changed their API policies and now **requires authentication** for most endpoints, including profile lookups. The initial design assumed public profile access, but that's no longer available.

## Solution Applied

✅ **Updated** `get_profile_info()` to use a donor account session  
✅ **Added** check for donor account availability  
✅ **Improved** error message to guide users  

## For Production Use

**Recommendation**: Keep at least **5-10 donor accounts** in the system to:
- Distribute API calls across accounts
- Avoid rate limiting
- Provide redundancy if some accounts fail

---

## Quick Test Command

After adding a donor account:

```bash
# Test profile lookup
curl -X POST http://localhost:5000/api/lookup-profile \
  -H "Content-Type: application/json" \
  -d '{"username":"instagram"}'
```

Should return:
```json
{
  "success": true,
  "profile": {
    "username": "instagram",
    "follower_count": 123456789,
    "is_private": false,
    ...
  }
}
```
