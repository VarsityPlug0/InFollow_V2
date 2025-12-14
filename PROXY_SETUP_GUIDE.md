# 🌐 Proxy Setup Guide - Fix Instagram IP Blacklist

## 🎯 **Why You Need This**

Render's shared IP addresses are blacklisted by Instagram. To make the system fully functional, you need to route Instagram requests through residential proxies.

---

## 📋 **Step-by-Step Setup**

### **Step 1: Get a Proxy Service**

Choose one of these providers:

| Provider | Monthly Cost | Quality | Link |
|----------|-------------|---------|------|
| **Bright Data** | $500+ | ⭐⭐⭐⭐⭐ Best | https://brightdata.com |
| **Smartproxy** | $50+ | ⭐⭐⭐⭐ Good | https://smartproxy.com |
| **IPRoyal** | $30+ | ⭐⭐⭐ Budget | https://iproyal.com |
| **Webshare** | $25+ | ⭐⭐⭐ Budget | https://webshare.io |

**Recommended:** Start with **Smartproxy** or **IPRoyal** for testing.

---

### **Step 2: Get Your Proxy Credentials**

After signing up, you'll receive:

```
Proxy Host: gate.smartproxy.com
Proxy Port: 7000
Username: your_username
Password: your_password
```

---

### **Step 3: Configure on Render**

1. Go to your Render dashboard
2. Click on your `infollow-v2` service
3. Go to **Environment** tab
4. Click **"Add Environment Variable"**

Add these 4 variables:

```
PROXY_HOST = gate.smartproxy.com
PROXY_PORT = 7000
PROXY_USERNAME = your_username
PROXY_PASSWORD = your_password
```

5. Click **"Save Changes"**
6. Your app will automatically redeploy

---

### **Step 4: Verify It's Working**

After redeployment, check the Render logs. You should see:

```
[INSTAGRAPI] 🌐 Proxy configured: gate.smartproxy.com:7000
[INSTAGRAPI] Using proxy for this request
```

Instead of:
```
[INSTAGRAPI] ⚠️ No proxy configured - using direct connection
```

---

## 🧪 **Test the System**

### **1. Test Profile Lookup:**

Visit your app and try to lookup a profile. Check logs:

```
[LOOKUP] Fetching profile for @username...
[INSTAGRAPI] 🌐 Proxy configured: gate.smartproxy.com:7000
[INSTAGRAPI] Using proxy for this request
[INSTAGRAPI] ✓ Profile fetched: @username (1234 followers)
```

✅ If you see real follower counts, it's working!

### **2. Test Account Donation:**

1. Go to `/donate`
2. Add a test Instagram account
3. Check logs for successful login through proxy

### **3. Test Follower Delivery:**

1. Claim free followers
2. Check logs for successful follows
3. Verify followers appear on target account

---

## 💰 **Cost Breakdown**

### **Residential Proxies:**

- **Smartproxy**: ~$50/month for 5GB
- **IPRoyal**: ~$30/month for 5GB
- **Bright Data**: ~$500/month for premium quality

### **Datacenter Proxies (Cheaper but less reliable):**

- **Webshare**: $25/month for 10 proxies
- May still get blocked by Instagram

---

## 🔧 **Alternative: Run Locally**

If you don't want to pay for proxies:

### **Option A: Run on Your Computer**

1. Clone the repo to your local machine
2. Run: `python app.py`
3. Your home IP is likely not blacklisted
4. Access at `http://localhost:5000`

### **Option B: Deploy to VPS with Clean IP**

1. Get a VPS (DigitalOcean, Linode, Vultr)
2. Deploy your app there
3. VPS IPs are usually clean

---

## 📊 **Proxy Configuration Details**

### **How It Works:**

1. Your app detects proxy environment variables
2. Creates Instagram clients with proxy settings
3. All Instagram requests route through the proxy
4. Instagram sees the proxy's IP (not Render's blacklisted IP)

### **Code Changes Made:**

✅ **`config.py`**: Added proxy configuration
✅ **`instagram.py`**: Updated to use proxies
✅ **All Instagram API calls**: Now use proxy if configured

---

## 🚨 **Troubleshooting**

### **Issue: Proxy not working**

**Check logs for:**
```
[INSTAGRAPI] ⚠️ No proxy configured - using direct connection
```

**Solution**: Verify environment variables are set correctly on Render.

---

### **Issue: Proxy connection failed**

**Error in logs:**
```
ProxyError: Cannot connect to proxy
```

**Solution**: 
- Verify proxy credentials
- Check proxy provider dashboard
- Ensure proxy service is active

---

### **Issue: Still getting IP blacklist error**

**Error:**
```
IP address added to the blacklist of the Instagram Server
```

**Solution**:
- Your proxy might be detected
- Switch to residential proxies (not datacenter)
- Try a different proxy provider

---

## 🎯 **Recommended Setup**

**For Testing:**
- Use **IPRoyal** or **Smartproxy**
- Start with smallest plan
- Test with 1-2 accounts

**For Production:**
- Use **Bright Data** or **Smartproxy**
- Residential proxies only
- Rotate IPs for each request

---

## 📝 **Next Steps**

1. ✅ Sign up for proxy service
2. ✅ Get credentials
3. ✅ Add to Render environment variables
4. ✅ Wait for auto-deployment
5. ✅ Test profile lookup
6. ✅ Test follower delivery
7. ✅ Monitor logs for success

---

## ⚡ **Quick Start Commands**

### **Test locally with proxy:**

```bash
# Set environment variables
export PROXY_HOST=gate.smartproxy.com
export PROXY_PORT=7000
export PROXY_USERNAME=your_username
export PROXY_PASSWORD=your_password

# Run app
python app.py
```

### **Check if proxy is working:**

Visit: `http://localhost:5000`
Try lookup: Any Instagram username
Check console output for proxy messages

---

**Your system will be fully functional once proxies are configured!** 🚀
