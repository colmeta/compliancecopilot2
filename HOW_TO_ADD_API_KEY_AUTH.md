# How to Add API Key Authentication to CLARITY

**Optional: Only do this if you want to restrict access to your API**

---

## 🔑 Your API Key

```
CLARITY_API_KEY=QmlSn68qp7tXGv0EdqMiX41Qqo8LlRPI5J4W2cawPcA
```

**Save this securely!** You'll need it to access your API.

---

## 📋 Setup Instructions

### Step 1: Add Key to Render

1. Go to https://dashboard.render.com
2. Select your `veritas-engine` service
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Set:
   ```
   Key: CLARITY_API_KEY
   Value: QmlSn68qp7tXGv0EdqMiX41Qqo8LlRPI5J4W2cawPcA
   ```
6. Click **Save Changes**
7. Render will auto-redeploy

---

### Step 2: Protect Your Routes (Optional)

**File:** `app/api/real_analysis_routes.py`

**Add authentication to specific routes:**

```python
from app.middleware.auth import require_api_key

@real_analysis.route('/real/analyze', methods=['POST'])
@require_api_key  # Add this line
def analyze():
    # ... existing code ...
```

**Protect all routes in a blueprint:**

```python
from app.middleware.auth import require_api_key

# Apply to all routes in this blueprint
real_analysis.before_request(require_api_key)
```

---

## 🧪 Testing with API Key

### Without Key (Will Fail)

```bash
curl -X POST https://veritas-engine-zae0.onrender.com/real/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Test",
    "domain": "legal",
    "document_content": "Test"
  }'
```

**Response:**
```json
{
  "error": "Unauthorized",
  "message": "Valid API key required",
  "status": 401
}
```

---

### With Key (Will Work)

**Option 1: X-API-KEY header**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/real/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: QmlSn68qp7tXGv0EdqMiX41Qqo8LlRPI5J4W2cawPcA" \
  -d '{
    "directive": "Test",
    "domain": "legal",
    "document_content": "Test"
  }'
```

**Option 2: Authorization header**
```bash
curl -X POST https://veritas-engine-zae0.onrender.com/real/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer QmlSn68qp7tXGv0EdqMiX41Qqo8LlRPI5J4W2cawPcA" \
  -d '{
    "directive": "Test",
    "domain": "legal",
    "document_content": "Test"
  }'
```

---

## 🔐 For MCP Server Users

**Update their config to include the key:**

**File:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "clarity-engine": {
      "command": "node",
      "args": ["/path/to/mcp-server/server.js"],
      "env": {
        "CLARITY_API_URL": "https://veritas-engine-zae0.onrender.com",
        "CLARITY_API_KEY": "QmlSn68qp7tXGv0EdqMiX41Qqo8LlRPI5J4W2cawPcA"
      }
    }
  }
}
```

**Update MCP server code:**

**File:** `mcp-server/server.js`

Find:
```javascript
const options = {
  method,
  headers: {
    "Content-Type": "application/json",
    ...(API_KEY && { "X-API-KEY": API_KEY }),
  },
};
```

Already supports it! Just set the env variable.

---

## 💰 Charging Customers

**With API keys, you can:**

1. **Generate unique keys per customer**
2. **Track usage per key**
3. **Revoke access** if they stop paying
4. **Rate limit** per key

### Generate More Keys

```bash
# Generate a new key for each customer
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example:**
- Customer A: `key_abc123...`
- Customer B: `key_xyz789...`
- Customer C: `key_def456...`

Store in database with:
- Customer ID
- Key
- Usage count
- Last used
- Active/Inactive status

---

## 🚨 Current Status

**Right now:**
- ✅ Your API is **OPEN** (no key required)
- ✅ Good for testing
- ✅ Good for demos
- ⚠️  Anyone can use it

**After adding key:**
- ✅ API is **PROTECTED**
- ✅ Only authorized users
- ✅ Track who's using it
- ✅ Can revoke access

---

## ❓ Should You Add This Now?

**Add it NOW if:**
- ✅ You're going live with customers
- ✅ You want to track usage
- ✅ You need security

**Wait if:**
- ⏳ Still testing/developing
- ⏳ Just showing demos
- ⏳ Only you are using it

---

## 🎯 Recommendation

**For now:** Don't add it (keep API open for testing)

**When ready to launch:** 
1. Add the key to Render
2. Update routes to require it
3. Give key to customers
4. Track usage

---

**Your key is saved in this document. Keep it secure!** 🔐
