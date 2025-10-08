# 🚀 Deployment Steps - Session-Based Authentication

## ✅ Current Status

### Local Testing: COMPLETE ✅
- ✅ Webhook server runs on `localhost:8002`
- ✅ Session creation works
- ✅ Authentication with sid works
- ✅ Device control with auth check works

### Code Status:
- ✅ All changes committed to git
- ✅ Branch: `004-llm-rag-based`
- ⏳ Needs deployment to Railway

## 📋 Next Steps to Deploy

### Option 1: Railway Dashboard (RECOMMENDED - Easiest)

1. **Open Railway Dashboard:**
   - Go to: https://railway.app/dashboard
   - Login with your account

2. **Find Your Project:**
   - Look for project: **healthy-alley**
   - Click on it

3. **Trigger Redeploy:**
   - Click on the service (webhook service)
   - Go to **Deployments** tab
   - Click **Deploy** or **Redeploy**
   - OR: Go to **Settings** → click **Redeploy**

4. **Wait for deployment** (1-2 minutes)

5. **Verify deployment:**
   ```bash
   curl https://healthy-alley-production.up.railway.app/
   ```
   Should return: `{"service":"VAPI Auth Webhook","status":"healthy","version":"2.0.0"}`

### Option 2: GitHub Auto-Deploy (if configured)

If Railway is connected to your GitHub repo:

```bash
# Push changes
git push origin 004-llm-rag-based
```

Railway will auto-deploy when it detects the push.

### Option 3: Railway CLI (Interactive)

```bash
cd webhook_service

# Link to project (requires manual selection)
railway link
# Select: healthy-alley
# Select: production
# Select: your-service-name

# Deploy
railway up
```

## 🧪 Verify Railway Deployment

Once deployed, run these commands:

### 1. Check Health
```bash
curl https://healthy-alley-production.up.railway.app/health
```
Expected: `{"status":"healthy"}`

### 2. Check Version (New!)
```bash
curl https://healthy-alley-production.up.railway.app/
```
Expected: `{"service":"VAPI Auth Webhook","status":"healthy","version":"2.0.0"}`

### 3. Test Session Creation
```bash
curl -X POST https://healthy-alley-production.up.railway.app/sessions \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"urbanjungle","password":"alpha-bravo-123"}'
```
Expected: `{"sid":"<uuid>","authenticated":false}`

### 4. Test Authentication (use sid from step 3)
```bash
SID="<paste-sid-here>"

curl -X POST "https://healthy-alley-production.up.railway.app/auth?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{}'
```
Expected: `{"result":"{\"success\": true, \"message\": \"Welcome!...\"}"}`

## 🎤 Run VAPI Client

After Railway is deployed:

```bash
# Activate environment
source venv/bin/activate

# Run client
python src/vapi_client_clean.py
```

### Expected Output:

```
============================================================
🎤 VAPI Voice Assistant - Session Authentication
============================================================
👤 Customer: urbanjungle
🔐 Password: ***************
🌐 API Base: https://healthy-alley-production.up.railway.app
============================================================

🔑 Creating session...
✅ Session created: a1b2c3d4...

📞 Starting VAPI call with sid-based tools...
✅ Voice session started!
📱 Call ID: xxx
🔑 Session ID: a1b2c3d4...

============================================================
🔊 Luna will authenticate automatically
============================================================

🗣️  Start speaking after you hear Luna's greeting...
```

### What Happens:

1. **Luna says:** "Hi! Authenticating..."
2. **Luna calls `home_auth()` automatically**
3. **Luna says:** "Welcome! Authentication successful. I'm Luna, your smart home assistant. How can I help you today?"
4. **You say:** "Hey Luna, turn on the fan"
5. **Luna says:** "Fan on" (and calls the control endpoint)

## 🐛 Troubleshooting

### Railway Deployment Failed
- Check Railway logs in the dashboard
- Verify `requirements.txt` is correct
- Check `railway.json` configuration

### Session Creation Fails
```bash
# Check Railway logs
railway logs --service <your-service>
```

### Client Can't Connect
- Verify Railway URL is correct in `vapi_client_clean.py` line 31
- Should be: `https://healthy-alley-production.up.railway.app`

### Authentication Fails in VAPI
- Check Railway logs for `/auth` requests
- Verify sid is being passed in URL
- Check session was created successfully

## 📊 Current Files Modified

✅ `webhook_service/main.py` - Session-based auth endpoints
✅ `src/vapi_client_clean.py` - Updated client with sid support
✅ `SESSION_AUTH_SETUP.md` - Complete documentation
✅ `src/test_session_local.py` - Local testing script

## 🎯 Summary

**The implementation is COMPLETE and TESTED locally!**

All you need to do is:
1. Deploy to Railway via dashboard
2. Verify endpoints work (run the curl commands above)
3. Run the client: `python src/vapi_client_clean.py`
4. Say "Hey Luna, turn on the fan"

That's it! 🎉
