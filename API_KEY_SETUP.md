# VAPI API Key Setup

## Important: Public vs Private Keys

VAPI has **two types** of API keys:

### 1. Private API Key (Account Management)
- Used for: Creating/updating assistants, phone numbers, managing account
- **NOT** used for making calls
- Format: Usually starts with lowercase letters
- Example: `e4077034-d96a-41c7-8f49-e36accb11fb4`

### 2. Public API Key (Making Calls)
- Used for: Starting VAPI calls from client applications
- This is what we need for the proxy!
- Format: Usually longer, may start with different pattern
- **This is the one you need to set in Railway**

---

## How to Get Your Public API Key

1. Go to **VAPI Dashboard**: https://dashboard.vapi.ai
2. Click on **API Keys** (or **Settings** → **API Keys**)
3. Look for **"Public API Key"** or **"Client API Key"**
4. Copy the public key

---

## Update Railway Environment Variable

Once you have the **public API key**:

```bash
railway variables --set "VAPI_API_KEY=your-public-key-here"
```

Or via Railway dashboard:
1. Go to https://railway.app/project/glistening-clarity
2. Click on your service
3. **Variables** tab
4. Update `VAPI_API_KEY` with your **public key**
5. Save

---

## Current Status

✅ Secure proxy is deployed and working
✅ Device authentication is working
✅ JWT tokens are working
✅ Token refresh is working
⚠️ Need to update VAPI_API_KEY with **public key** (not private key)

---

## After Updating the Key

Test the complete flow:

```bash
./test_secure_proxy.sh
```

Or test with the secure client:

```bash
python3 src/vapi_client_secure_proxy.py
```

Expected: VAPI call starts successfully via secure proxy!
