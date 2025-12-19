# Brain/Hands Architecture Plan
## Instagram Donation System - Distributed Design

**Created:** 2025-12-14  
**For:** Bevan Mkhabele  

---

## 🎯 Overview

Split the Instagram donation system into two independent components:

- **Brain (Render):** Web app, user sessions, donations, credits, job queue
- **Hands (Windows PC → Ubuntu VPS):** Instagram actions, logins, follows, session management

---

## 📊 Architecture Decisions Summary

| # | Question | Answer |
|---|----------|--------|
| 1 | Brain Database | **Render Postgres** (~$7/mo, persists across deploys) |
| 2 | Brain IG Calls | **Local dev only** (Brain can call IG locally, never in production) |
| 3 | Hands Location | **Windows PC for testing → Ubuntu VPS for production** |
| 4 | Hands OS | **Ubuntu/Linux** (VPS deployment) |
| 5 | Communication | **Hands polls Brain** (outbound only, no firewall setup) |
| 6 | Accounts Managed | **Both** (system + donated accounts on Hands) |
| 7 | Session Storage | **JSON files** in `sessions/` folder on Hands |
| 8 | Proxies | **No proxies for local testing**, add when moving to VPS |
| 9 | Rate Limiting | **1 second delays** between follows |
| 10 | Real-Time Updates | **Keep Socket.IO** (Hands → Brain → User live streaming) |
| 11 | Job Queue | **Postgres `jobs` table** (simple, persisted) |
| 12 | Password Storage | **Plain text in Brain DB**, sent to Hands per job |
| 13 | System Account | **Environment variable** on Hands (`SYSTEM_IG_USERNAME/PASSWORD`) |
| 14 | Workforce Model | **Entire workforce** (all unused accounts per job) |
| 15 | Status Updates | **Direct DB updates** (Hands writes to Postgres) |
| 16 | Concurrency | **One job at a time** (sequential queue) |
| 17 | Failure Handling | **Retry 3x with backoff**, mark failed, notify user |
| 18 | Logging | **Both keep logs**; Hands sends execution logs to Brain |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       BRAIN (Render)                        │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Flask Web App (app.py)                               │ │
│  │  - User sessions, auth, donations                     │ │
│  │  - Profile lookup UI (no IG calls in prod)            │ │
│  │  - Socket.IO real-time updates                        │ │
│  │  - Job creation endpoints                             │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓ ↑                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Postgres Database (Render managed)                   │ │
│  │  - users, donated_accounts, targets, action_logs      │ │
│  │  - NEW: jobs table (id, status, target, tier, etc.)  │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↑ ↓                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Internal API (for Hands)                             │ │
│  │  GET  /internal/poll-jobs      → Fetch pending job   │ │
│  │  POST /internal/progress       → Stream live updates │ │
│  │  POST /internal/job-complete   → Mark job done       │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↑ (HTTPS polling every 5s)
                           │
┌─────────────────────────────────────────────────────────────┐
│                  HANDS (Windows PC / Ubuntu VPS)            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Worker Script (hands_worker.py)                      │ │
│  │  - Polls Brain for jobs                               │ │
│  │  - Executes Instagram follows                         │ │
│  │  - Sends progress updates to Brain                    │ │
│  │  - Updates DB directly (account status, logs)         │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓ ↑                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Instagram Automation (instagram.py)                  │ │
│  │  - System validation account (env var)                │ │
│  │  - Profile lookups                                    │ │
│  │  - Account verification                               │ │
│  │  - Follow execution (instagrapi Client)               │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Session Storage (sessions/ folder)                   │ │
│  │  - JSON files per Instagram account                   │ │
│  │  - Persisted across worker restarts                   │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Instagram API (via instagrapi)                       │ │
│  │  - Safe IP (home/VPS, optionally proxied)             │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### **1. User Requests Free Test (20 followers)**

```
User (Browser)
  → Brain: POST /api/claim-free-followers {username}
    → Check auth, free_test_used
    → Create Target record (tier='free_test')
    → Create Job record (status='pending')
    → Return: "Job queued"

Hands Worker (polling every 5s)
  → Brain: GET /internal/poll-jobs
    ← Brain: Job{id, target_username, tier, accounts: [...]}
  → Hands: Execute follows
    → For each account in workforce:
      → Login via instagrapi
      → Follow target
      → Send progress: POST /internal/progress {job_id, current, total}
      → Update DonatedAccount.status='used' (direct DB)
      → Log to ActionLog (direct DB)
  → Hands: POST /internal/job-complete {job_id, results}
    → Brain: Update Job.status='complete'
    → Brain: Emit Socket.IO final result to user

User (Browser)
  ← Socket.IO: Live progress updates
  ← Final: "Successfully delivered 20 followers!"
```

### **2. User Donates Account**

```
User (Browser)
  → Brain: POST /api/donate {username, password}
    → Brain: Create Job (type='verify_account')
    → Return: "Verifying account..."

Hands Worker
  → Brain: GET /internal/poll-jobs
    ← Job{type='verify', username, password}
  → Hands: instagram.verify_account(username, password)
    → Login via instagrapi
    → Save session to sessions/{username}.json
  → Success:
    → Insert DonatedAccount (status='unused', user_id=X)
    → Increment User.free_targets += 1
  → Fail:
    → Return error to Brain
  → POST /internal/job-complete

User (Browser)
  ← "Account verified! You earned 30 followers credit."
```

### **3. Profile Lookup**

**Local Dev (Brain running on your PC):**
```
User → Brain: POST /api/lookup-profile {username}
  → Brain: ig_automation.get_profile_info(username)
    → Direct instagrapi call (local IP safe)
  → Return profile data
```

**Production (Render):**
```
User → Brain: POST /api/lookup-profile {username}
  → Brain: Create Job (type='profile_lookup')
  → Hands polls, executes lookup via system account
  → Returns profile data to Brain
  → Brain returns to user
```

---

## 🗄️ Database Schema Changes

### **NEW: `jobs` Table**

```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,  -- 'follow', 'verify', 'profile_lookup'
    status VARCHAR(20) NOT NULL,     -- 'pending', 'processing', 'complete', 'failed'
    target_username VARCHAR(100),
    tier VARCHAR(20),                -- 'free_test', 'donation'
    user_id INTEGER REFERENCES users(id),
    payload JSONB,                   -- Additional job data (accounts, passwords, etc.)
    result JSONB,                    -- Job results
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created ON jobs(created_at);
```

### **Existing Tables (unchanged):**
- `users`
- `donated_accounts`
- `targets`
- `action_logs`

---

## 🔐 Security & Credentials

### **Brain (Render)**
**Environment Variables:**
```bash
SECRET_KEY=<random-secret>
ADMIN_PASSWORD=<admin-password>
DATABASE_URL=<postgres-connection-string>  # Managed by Render
HANDS_API_KEY=<shared-secret-for-hands>    # NEW: Authenticate Hands requests
```

**Stored Data:**
- User sessions (encrypted)
- Donated account passwords (plain text in DB, sent to Hands per job)
- NO Instagram credentials in code

### **Hands (Windows/Ubuntu)**
**Environment Variables:**
```bash
BRAIN_URL=https://infollow-v2.onrender.com
HANDS_API_KEY=<same-shared-secret>
DATABASE_URL=<same-postgres-connection-string>  # Read/write access
SYSTEM_IG_USERNAME=virg.ildebie
SYSTEM_IG_PASSWORD=ShadowTest31@

# Optional (for VPS with proxies):
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
PROXY_USERNAME=user
PROXY_PASSWORD=pass
```

**Stored Data:**
- Instagram session files (sessions/*.json)
- Execution logs (hands_worker.log)

---

## 📡 Brain Internal API Spec

### **1. Poll for Jobs**
```http
GET /internal/poll-jobs
Headers:
  X-Hands-API-Key: <HANDS_API_KEY>

Response 200:
{
  "job": {
    "id": 123,
    "job_type": "follow",
    "target_username": "example_user",
    "tier": "free_test",
    "accounts": [
      {"username": "donor1", "password": "pass1"},
      {"username": "donor2", "password": "pass2"}
    ]
  }
}

Response 204: No jobs available
```

### **2. Send Progress Update**
```http
POST /internal/progress
Headers:
  X-Hands-API-Key: <HANDS_API_KEY>
Content-Type: application/json

Body:
{
  "job_id": 123,
  "current": 5,
  "total": 20,
  "status": "Following with @donor5..."
}

Response 200: {"success": true}
```

### **3. Complete Job**
```http
POST /internal/job-complete
Headers:
  X-Hands-API-Key: <HANDS_API_KEY>
Content-Type: application/json

Body:
{
  "job_id": 123,
  "status": "complete",  // or "failed"
  "result": {
    "success": 18,
    "failed": 2,
    "errors": [...]
  }
}

Response 200: {"success": true}
```

---

## 🚀 Implementation Steps

### **Phase 1: Database & Brain Prep**
1. ✅ Upgrade Brain to Render Postgres
2. ✅ Create `jobs` table migration
3. ✅ Add internal API endpoints (`/internal/poll-jobs`, `/progress`, `/job-complete`)
4. ✅ Add API key authentication for Hands
5. ✅ Modify user-facing endpoints to create jobs instead of executing directly

### **Phase 2: Hands Worker**
6. ✅ Create `hands_worker.py` (polling script)
7. ✅ Move `instagram.py` to Hands
8. ✅ Update `instagram.py` to read system account from env vars
9. ✅ Implement job execution logic (follow, verify, lookup)
10. ✅ Add progress reporting to Brain
11. ✅ Add direct DB writes for account status & logs

### **Phase 3: Testing**
12. ✅ Test on Windows PC locally
13. ✅ Test Brain → Hands communication
14. ✅ Test Socket.IO real-time updates
15. ✅ Test failure handling & retries

### **Phase 4: VPS Deployment**
16. ✅ Set up Ubuntu VPS (DigitalOcean/Linode)
17. ✅ Install Python, dependencies, systemd service
18. ✅ Configure proxies (if needed)
19. ✅ Monitor logs & performance

---

## 🛠️ File Structure Changes

### **Brain (Render)**
```
InFollow/
├── app.py                    # Modified: create jobs, remove direct IG calls
├── models.py                 # Modified: add Job model
├── config.py                 # Modified: add HANDS_API_KEY
├── requirements.txt          # Remove instagrapi (Brain doesn't need it)
├── templates/
├── static/
├── Procfile
├── runtime.txt
└── migrations/               # NEW: Postgres migrations
    └── 001_add_jobs_table.sql
```

### **Hands (Worker)**
```
hands_node/
├── hands_worker.py           # NEW: Main polling worker
├── instagram.py              # MOVED from Brain
├── config.py                 # NEW: Hands-specific config
├── requirements.txt          # instagrapi, psycopg2, requests
├── sessions/                 # Instagram session files
├── .env                      # Local env vars
└── systemd/                  # NEW: Service file for Ubuntu
    └── hands-worker.service
```

---

## ⚡ Performance & Reliability

### **Polling Frequency**
- Hands polls Brain every **5 seconds**
- Low overhead, near-instant job pickup

### **Job Processing**
- **Sequential:** One job at a time (avoids account conflicts)
- **Rate limiting:** 1 second between follows
- **Execution time:** ~20-30 seconds for 20 accounts

### **Failure Handling**
1. Job fails → increment `retry_count`
2. Retry with exponential backoff (5s, 15s, 45s)
3. After 3 failures → mark `status='failed'`, notify user

### **Database Load**
- Brain: Mostly reads (user sessions, job queue)
- Hands: Writes (account status, logs, job results)
- Postgres handles both easily at low-medium scale

---

## 📈 Scaling Path

### **Current (Testing):**
- 1 Brain instance (Render)
- 1 Hands worker (your PC)
- ~100 accounts, ~10 users

### **Phase 2 (Production):**
- 1 Brain instance (Render)
- 1 Hands worker (Ubuntu VPS)
- Proxies enabled
- ~500 accounts, ~50 users

### **Phase 3 (Growth):**
- 1-2 Brain instances (Render horizontal scaling)
- 2-3 Hands workers (multiple VPS, round-robin job distribution)
- Redis queue (replace Postgres jobs table)
- ~2000 accounts, ~200 users

---

## 🔍 Monitoring & Logs

### **Brain Logs**
- Job creation: `[JOB] Created follow job #123 for @target`
- Progress relay: `[PROGRESS] Job #123: 5/20 complete`
- Completion: `[JOB] Job #123 completed: 18 success, 2 failed`

### **Hands Logs**
- Polling: `[POLL] Checking for jobs... (none)`
- Execution: `[EXECUTE] Job #123: Following @target with 20 accounts`
- Progress: `[FOLLOW] [5/20] @donor5 → @target ✓`
- Errors: `[ERROR] Job #123 failed: Instagram rate limit`

### **Centralized Monitoring**
- Brain stores all execution logs in ActionLog table
- Hands sends structured log data via `/internal/progress`
- Admin dashboard shows real-time worker status

---

## ✅ Success Criteria

- ✅ Brain deploys to Render with zero Instagram code
- ✅ Hands runs on Windows PC, then migrates to Ubuntu VPS
- ✅ Users see real-time progress during follow execution
- ✅ Account donations are verified on Hands, never on Brain
- ✅ Profile lookups work in both local dev and production
- ✅ System handles failures gracefully (retry, notify)
- ✅ No data loss across Brain redeployments (Postgres)
- ✅ Hands can be stopped/restarted without losing jobs
- ✅ Easy to add proxies when moving to VPS

---

## 🎯 Next Steps

**Ready to implement?** I'll start with:

1. Create Postgres migration for `jobs` table
2. Add internal API endpoints to Brain
3. Create `hands_worker.py` script
4. Update `app.py` to create jobs instead of direct execution
5. Test locally with your Windows PC

**Let me know when to proceed!** 🚀
