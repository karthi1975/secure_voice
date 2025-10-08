# Deploy to Railway

## Option 1: Via Railway Dashboard (Recommended)

1. Go to https://railway.app/dashboard
2. Find project: **healthy-alley**
3. Click on the service
4. Go to **Settings** → **Source**
5. Click **Redeploy** or **Deploy Latest**

OR

6. Railway will auto-deploy on git push if GitHub integration is set up

## Option 2: Via Git Push (if connected)

```bash
cd /Users/karthi/business/tetradapt/secure_voice
git add webhook_service/main.py
git commit -m "feat: session-based auth with sid parameter"
git push origin 004-llm-rag-based
```

Railway will automatically deploy if GitHub integration is enabled.

## Option 3: Manual Railway CLI Deploy

```bash
cd webhook_service

# Link to project (interactive)
railway link

# Select: healthy-alley project
# Select: production environment
# Select: <service-name>

# Deploy
railway up
```

## Verify Deployment

```bash
# Check health
curl https://healthy-alley-production.up.railway.app/health

# Should return: {"status":"healthy"}

# Check version (new endpoint returns version 2.0.0)
curl https://healthy-alley-production.up.railway.app/

# Should return: {"service":"VAPI Auth Webhook","status":"healthy","version":"2.0.0"}
```

## Test New Endpoints

```bash
# Create session
curl -X POST https://healthy-alley-production.up.railway.app/sessions \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"urbanjungle","password":"alpha-bravo-123"}'

# Should return: {"sid":"<uuid>","authenticated":false}
```
