# Hands Worker Setup & Usage Guide

## 🎯 Overview

The **Hands Worker** is a standalone Python script that polls the Brain (Render) for jobs and executes Instagram actions on a safe IP address.

---

## 🖥️ Running on Windows PC (Testing)

### **Step 1: Navigate to Project**
```powershell
cd c:\Users\money\HustleProjects\InFollow
```

### **Step 2: Set Environment Variables**
```powershell
$env:BRAIN_URL="http://localhost:5000"
$env:HANDS_API_KEY="dev-hands-key-change-in-production"
$env:DATABASE_URL="sqlite:///barter.db"
$env:SYSTEM_IG_USERNAME="virg.ildebie"
$env:SYSTEM_IG_PASSWORD="ShadowTest31@"
```

**For Production (Brain on Render):**
```powershell
$env:BRAIN_URL="https://your-app.onrender.com"
$env:DATABASE_URL="postgresql://user:pass@host:5432/dbname"  # Get from Render
$env:HANDS_API_KEY="your-actual-api-key"  # Must match Brain
```

### **Step 3: Run Worker**
```powershell
python hands_worker.py
```

You should see:
```
[2025-12-14 15:00:00] ============================================================
[2025-12-14 15:00:00] 🚀 Hands Worker Starting
[2025-12-14 15:00:00] 🧠 Brain URL: http://localhost:5000
[2025-12-14 15:00:00] 📊 Database: SQLite
[2025-12-14 15:00:00] 📸 System Account: @virg.ildebie
[2025-12-14 15:00:00] ⏱️  Poll Interval: 5s
[2025-12-14 15:00:00] ============================================================
```

---

## 🐧 Running on Ubuntu VPS (Production)

### **Step 1: Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Create project directory
mkdir -p /opt/hands_worker
cd /opt/hands_worker
```

### **Step 2: Upload Files**
Upload these files to `/opt/hands_worker/`:
- `hands_worker.py`
- `instagram.py`
- `models.py`
- `config.py`
- `requirements.txt`

### **Step 3: Install Python Dependencies**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Step 4: Create Environment File**
```bash
nano .env
```

Add:
```bash
BRAIN_URL=https://your-app.onrender.com
HANDS_API_KEY=your-hands-api-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SYSTEM_IG_USERNAME=virg.ildebie
SYSTEM_IG_PASSWORD=ShadowTest31@

# Optional: Proxies
# PROXY_HOST=proxy.example.com
# PROXY_PORT=8080
# PROXY_USERNAME=user
# PROXY_PASSWORD=pass
```

### **Step 5: Create Systemd Service**
```bash
sudo nano /etc/systemd/system/hands-worker.service
```

Add:
```ini
[Unit]
Description=InFollow Hands Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hands_worker
EnvironmentFile=/opt/hands_worker/.env
ExecStart=/opt/hands_worker/venv/bin/python3 /opt/hands_worker/hands_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Step 6: Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable hands-worker
sudo systemctl start hands-worker
```

### **Step 7: Check Status**
```bash
sudo systemctl status hands-worker
sudo journalctl -u hands-worker -f  # Follow logs
```

---

## 🔧 Configuration

### **Environment Variables**

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BRAIN_URL` | ✅ | Brain (Render) URL | `https://infollow.onrender.com` |
| `HANDS_API_KEY` | ✅ | Shared secret for auth | `your-secret-key` |
| `DATABASE_URL` | ✅ | Postgres connection string | `postgresql://...` |
| `SYSTEM_IG_USERNAME` | ✅ | Instagram validation account | `virg.ildebie` |
| `SYSTEM_IG_PASSWORD` | ✅ | Instagram validation password | `ShadowTest31@` |
| `PROXY_HOST` | ❌ | Proxy server host | `proxy.example.com` |
| `PROXY_PORT` | ❌ | Proxy server port | `8080` |
| `PROXY_USERNAME` | ❌ | Proxy username | `user` |
| `PROXY_PASSWORD` | ❌ | Proxy password | `pass` |

---

## 📊 Monitoring

### **Check Worker Status**
```bash
# Systemd service status
sudo systemctl status hands-worker

# Recent logs
sudo journalctl -u hands-worker -n 50

# Follow live logs
sudo journalctl -u hands-worker -f
```

### **Stop/Restart Worker**
```bash
# Stop
sudo systemctl stop hands-worker

# Restart
sudo systemctl restart hands-worker

# Reload configuration
sudo systemctl daemon-reload
```

---

## 🐛 Troubleshooting

### **Worker not connecting to Brain**
- Check `BRAIN_URL` is correct
- Verify `HANDS_API_KEY` matches Brain
- Test Brain reachability: `curl -v https://your-app.onrender.com`

### **Database connection errors**
- Verify `DATABASE_URL` is correct
- Check Postgres is accessible from Hands IP
- Test: `psql $DATABASE_URL`

### **Instagram login failures**
- Check `SYSTEM_IG_USERNAME` and `SYSTEM_IG_PASSWORD`
- Verify Instagram account is not locked/challenged
- Consider using proxies if IP is blacklisted

### **No jobs being processed**
- Check Brain is creating jobs (check Brain logs)
- Verify worker is polling successfully
- Check `jobs` table in database: `SELECT * FROM jobs WHERE status='pending';`

---

## 🔐 Security

- ✅ API key authentication (Hands → Brain)
- ✅ Environment variables for secrets
- ✅ Direct database access (Hands writes account status & logs)
- ⚠️ Passwords stored plain text in DB (acceptable for donated accounts)
- 🔒 Use HTTPS for Brain URL in production

---

## 📈 Performance

- **Polling Interval:** 5 seconds
- **Rate Limiting:** 1 second between follows
- **Concurrency:** One job at a time (sequential processing)
- **Session Caching:** Instagram sessions saved as JSON files

---

## ✅ Next Steps

1. **Test locally:** Run worker on Windows PC with Brain running locally
2. **Deploy Brain to Render:** Add Postgres, set environment variables
3. **Set up VPS:** Install worker on Ubuntu VPS with systemd service
4. **Add proxies (optional):** Configure residential proxies for safety
5. **Monitor:** Watch logs and job completion rates

---

## 📞 Support

For issues or questions, review:
- [BRAIN_HANDS_ARCHITECTURE.md](./BRAIN_HANDS_ARCHITECTURE.md) - Full architecture docs
- Brain logs on Render
- Hands logs via `journalctl`
