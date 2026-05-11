# VeriJust API - Postman Testing Guide

## Setup

### 1. Install Postman
- Download from https://www.postman.com/downloads/
- Create a free account

### 2. Create a Postman Collection
1. Open Postman
2. Click **Collections** → **Create New** → **Collection**
3. Name it: `VeriJust API`
4. Click **Create**

---

## Step 1: Set Up Environment Variables

Environment variables will store your API URL and token, so you don't repeat them.

### Create Environment
1. Click **Environments** (left sidebar)
2. Click **Create New** → **Environment**
3. Name: `VeriJust Local`
4. Add variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `api_url` | `http://localhost:8000` | `http://localhost:8000` |
| `token` | ` ` | (will be populated after first request) |
| `guest_name` | `Guest User` | `Guest User` |
| `evidence_id` | ` ` | (will get from upload response) |
| `task_id` | ` | (will get from upload response) |
| `case_id` | ` ` | (optional, for case-based queries) |

5. Click **Save**
6. Make sure it's selected in the dropdown (top right)

---

## Step 2: Test Guest Token Endpoint

### Create Request
1. In your collection, click **+** to add a new request
2. Name: `01 - Get Guest Token`
3. Method: **POST**
4. URL: `{{api_url}}/api/v1/auth/guest`

### Headers
| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |

### Body (raw JSON)
```json
{
  "name": "{{guest_name}}"
}
```

### Tests (Auto-save token)
Click the **Tests** tab and add this script:

```javascript
if (pm.response.code === 200) {
  var jsonData = pm.response.json();
  pm.environment.set("token", jsonData.access_token);
  console.log("✓ Token saved: " + jsonData.access_token.substring(0, 20) + "...");
}
```

### Send
1. Click **Send**
2. You should see:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "saved": true
   }
   ```
3. The `token` variable is now populated automatically

---

## Step 3: Test Protected Routes

### 3a. Get User Profile

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/users/profile`
- Name: `02 - Get User Profile`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Send** → Should return:
```json
{
  "id": "...",
  "name": "Guest User",
  "full_name": "Guest User",
  "email": null,
  "is_guest": true,
  "organization_name": null,
  "tier": "guest",
  "is_active": true,
  "created_at": "2026-02-23T10:30:00"
}
```

### 3b. Get Evidence List

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/forensics/evidence?limit=10&offset=0`
- Name: `03 - List Evidence Files`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Send** → Returns list of evidence files (empty initially)

### 3c. Upload Evidence File

**Request:**
- Method: **POST**
- URL: `{{api_url}}/api/v1/forensics/upload`
- Name: `04 - Upload Evidence`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Body:** Select `form-data`
| Key | Value | Type |
|-----|-------|------|
| `file` | (select audio file) | File |
| `case_id` | (optional UUID) | Text |

**Tests Tab:**
```javascript
if (pm.response.code === 200) {
  var jsonData = pm.response.json();
  pm.environment.set("evidence_id", jsonData.evidence_id);
  pm.environment.set("task_id", jsonData.task_id);
  console.log("✓ Evidence ID: " + jsonData.evidence_id);
  console.log("✓ Task ID: " + jsonData.task_id);
}
```

**Send** → Should return:
```json
{
  "evidence_id": "e1234567-89ab-cdef-0123-456789abcdef",
  "task_id": "t1234567-89ab-cdef-0123-456789abcdef",
  "status": "processing",
  "message": "File 'evidence.mp3' uploaded. Analysis started."
}
```

### 3d. Get Analysis Results

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/forensics/analysis/{{evidence_id}}`
- Name: `05 - Get Analysis Results`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Send** → Returns analysis status and metrics

### 3e. Get Transcript

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/forensics/transcript/{{evidence_id}}`
- Name: `06 - Get Transcript`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Send** → Returns transcript segments with timestamps

### 3f. Get Task Status

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/forensics/task-status/{{task_id}}`
- Name: `07 - Get Task Status`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Send** → Returns task progress (pending/started/completed/failed)

### 3g. Get Cases

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/users/cases`
- Name: `08 - Get Cases`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Send** → Returns list of cases

### 3h. Create Case (Non-Guest Users Only)

**Request:**
- Method: **POST**
- URL: `{{api_url}}/api/v1/users/cases`
- Name: `09 - Create Case`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |
| `Content-Type` | `application/json` |

**Body (raw JSON):**
```json
{
  "title": "Case #2026-001",
  "description": "Evidence analysis case",
  "client_name": "Law Enforcement",
  "case_number": "CASE-2026-001"
}
```

**Expected Response (Guest):**
```json
{
  "detail": "Guest users cannot create cases"
}
```

### 3i. Delete Evidence

**Request:**
- Method: **DELETE**
- URL: `{{api_url}}/api/v1/forensics/evidence/{{evidence_id}}`
- Name: `10 - Delete Evidence`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Send** → Returns deletion confirmation

---

## Step 4: Test Error Scenarios

### 4a. Missing Token (401)

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/forensics/evidence`
- Name: `11 - Missing Token Error`

**DO NOT add** Authorization header

**Send** → Should return:
```json
{
  "detail": "Not authenticated"
}
```

### 4b. Invalid Token (401)

**Request:**
- Method: **GET**
- URL: `{{api_url}}/api/v1/forensics/evidence`
- Name: `12 - Invalid Token Error`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer invalid_token_xyz` |

**Send** → Should return:
```json
{
  "detail": "Could not validate credentials"
}
```

### 4c. Expired Token

1. Get a guest token
2. Wait 15+ minutes (or modify token payload)
3. Try to use it

**Send** → Should return 401

### 4d. Invalid File Type (400)

**Request:**
- Method: **POST**
- URL: `{{api_url}}/api/v1/forensics/upload`
- Name: `13 - Invalid File Type Error`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Body:** form-data
| Key | Value | Type |
|-----|-------|------|
| `file` | (select a .txt or .pdf file) | File |

**Send** → Should return:
```json
{
  "detail": "Invalid file type. Allowed: .mp3, .wav, .m4a, .mp4, .mov"
}
```

### 4e. File Too Large (Guest Limit)

**Request:**
- Method: **POST**
- URL: `{{api_url}}/api/v1/forensics/upload`
- Name: `14 - File Size Limit Error`

**Headers:**
| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

**Body:** form-data with file > 5MB

**Send** → Should return 403:
```json
{
  "detail": "Demo limit exceeded: Max file size is 5MB. Please upgrade."
}
```

---

## Step 5: Complete Test Flow

Here's the recommended order to test everything:

1. ✅ **01 - Get Guest Token** — Get token
2. ✅ **02 - Get User Profile** — Verify token works
3. ✅ **03 - List Evidence Files** — Check empty list
4. ✅ **04 - Upload Evidence** — Get evidence_id & task_id
5. ✅ **05 - Get Analysis Results** — Check status
6. 🔄 **07 - Get Task Status** (Repeat) — Monitor progress
7. ✅ **06 - Get Transcript** — Get transcript when complete
8. ✅ **08 - Get Cases** — List cases
9. ✅ **09 - Create Case** — Test guest restriction
10. ✅ **10 - Delete Evidence** — Clean up
11. ✅ **11-14 - Error Tests** — Validate error handling

---

## Advanced: Create Test Scripts

### Auto-run All Tests

1. Create a new **Request** named "Collection Runner"
2. In Postman, go to **Collections** → Your collection → **...** → **Run**
3. Select all requests
4. Click **Run**
5. Watch all tests execute sequentially

### Pre-request Script (Optional)

For any request, add a **Pre-request Script** to validate variables:

```javascript
// Check if token exists
if (!pm.environment.get("token")) {
  console.warn("⚠️ Token not set! Run 'Get Guest Token' first.");
}

// Log current environment
console.log("API URL: " + pm.environment.get("api_url"));
console.log("Token: " + pm.environment.get("token").substring(0, 20) + "...");
```

### Test Assertions

Add to any request's **Tests** tab:

```javascript
// Assert status code
pm.test("Status is 200", function () {
  pm.response.to.have.status(200);
});

// Assert response has token
pm.test("Response has access_token", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData).to.have.property("access_token");
});

// Assert guest flag
pm.test("User is guest", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData.is_guest).to.equal(true);
});

// Assert evidence list exists
pm.test("Response is an array", function () {
  pm.expect(pm.response.json()).to.be.an("array");
});
```

---

## Debugging Tips

### View Request/Response Details

1. Click **Send**
2. Check **Response** section:
   - **Body** — JSON response
   - **Headers** — Response headers
   - **Tests** — Test results (✓/✗)

### Enable Postman Console

1. Click **View** → **Show Postman Console** (bottom)
2. See all logs from your test scripts

### Check Token Contents

1. Go to https://jwt.io
2. Paste token (without `Bearer `)
3. See decoded payload:
   ```json
   {
     "sub": "Guest User",
     "jti": "...",
     "exp": 1708696800
   }
   ```

### Monitor Network

1. Backend logs: Check terminal running backend
2. Frontend logs: Open browser DevTools (F12)

---

## Import Postman Collection (Optional)

Save this JSON as `verijust-api.postman_collection.json`:

```json
{
  "info": {
    "name": "VeriJust API",
    "description": "Token-based forensic analysis API",
    "version": "1.0"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{token}}",
        "type": "string"
      }
    ]
  },
  "item": [
    {
      "name": "01 - Get Guest Token",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"name\": \"{{guest_name}}\"}"
        },
        "url": {
          "raw": "{{api_url}}/api/v1/auth/guest",
          "host": ["{{api_url}}"],
          "path": ["api", "v1", "auth", "guest"]
        }
      }
    },
    {
      "name": "02 - Get User Profile",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "{{api_url}}/api/v1/users/profile",
          "host": ["{{api_url}}"],
          "path": ["api", "v1", "users", "profile"]
        }
      }
    },
    {
      "name": "03 - List Evidence Files",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "{{api_url}}/api/v1/forensics/evidence?limit=10&offset=0",
          "host": ["{{api_url}}"],
          "path": ["api", "v1", "forensics", "evidence"],
          "query": [
            {
              "key": "limit",
              "value": "10"
            },
            {
              "key": "offset",
              "value": "0"
            }
          ]
        }
      }
    }
  ]
}
```

Then import:
1. Click **File** → **Import**
2. Select the JSON file
3. Done! All requests are set up

---

## Summary

| Step | Purpose | Method | Endpoint |
|------|---------|--------|----------|
| 1 | Get token | POST | `/api/v1/auth/guest` |
| 2 | Verify auth | GET | `/api/v1/users/profile` |
| 3 | List files | GET | `/api/v1/forensics/evidence` |
| 4 | Upload file | POST | `/api/v1/forensics/upload` |
| 5 | View results | GET | `/api/v1/forensics/analysis/{id}` |
| 6 | Get transcript | GET | `/api/v1/forensics/transcript/{id}` |
| 7 | Monitor task | GET | `/api/v1/forensics/task-status/{id}` |
| 8 | List cases | GET | `/api/v1/users/cases` |
| 9 | Test restrictions | POST | `/api/v1/users/cases` |
| 10 | Clean up | DELETE | `/api/v1/forensics/evidence/{id}` |

---

## Common Issues

### "Not authenticated" (401)
- ✅ Make sure `Authorization: Bearer {{token}}` header is present
- ✅ Run "Get Guest Token" first
- ✅ Token may have expired (15 min limit for guests)

### "Could not validate credentials" (401)
- ✅ Token is malformed or invalid
- ✅ Check the token value in Environment
- ✅ Regenerate by running "Get Guest Token"

### "Invalid file type" (400)
- ✅ Upload `.mp3`, `.wav`, `.m4a`, `.mp4`, or `.mov` files
- ✅ Check file extension

### "Demo limit exceeded" (403)
- ✅ File is > 5MB
- ✅ Guest users have this restriction
- ✅ Regular users will not have this limit

---

