# Backend Authentication & Token Middleware Implementation

## Overview

This document explains the complete token-based authentication system for the VeriJust FastAPI backend.

---

## Architecture

### 1. Dependencies Layer (`app/core/dependencies.py`)

**Purpose:** Validate tokens and return user context

**Key Function: `get_current_user(token, db)`**
- Extracts token from `Authorization: Bearer <token>` header
- Attempts JWT decode first (regular users)
- Falls back to guest_tokens table lookup (demo/guest users)
- Returns `UserContext` with:
  - `id`: UUID or guest token ID
  - `name`: User name
  - `is_guest`: Boolean flag
  - `is_demo`: Boolean flag (true for guests/demo users)
  - `scopes`: List of permissions

**Flow:**
```
┌─────────────────────────────────────┐
│ Route Handler                       │
│ Depends(get_current_user)           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ get_current_user(token, db)         │
├─────────────────────────────────────┤
│ 1. Extract token from header        │
│ 2. Try JWT decode                   │
│    ├─ Success → Return UserContext  │
│    └─ Fail → Try guest lookup       │
│ 3. Query guest_tokens table         │
│    ├─ Found & valid → Return        │
│    └─ Not found → 401 Error         │
└─────────────────────────────────────┘
```

---

### 2. Protected Routes

All protected routes follow this pattern:

```python
@router.get("/endpoint")
async def endpoint_handler(
    user: UserContext = Depends(get_current_user),  # ← Token validation
    db: Session = Depends(db_session.get_db)        # ← Database access
):
    # Now 'user' contains the authenticated user context
    if user.is_guest:
        # Handle guest-specific logic
        pass
    
    # Query database using user context
    db.query(models.Evidence).filter(...).all()
```

---

## Route Protection Strategy

### Category 1: Public Routes (No Auth)
- `POST /api/v1/auth/guest` — Create guest token
- `GET /` — Health check
- `GET /health` — API status

### Category 2: Protected Routes (Require Token)

#### Authentication Routes (`/api/v1/auth/*`)
- Already handled (see above)

#### Forensics Routes (`/api/v1/forensics/*`)
- `POST /upload` — Upload evidence
- `GET /evidence` — List evidence files
- `GET /evidence/{id}` — Get evidence details
- `GET /analysis/{id}` — Get analysis results
- `GET /transcript/{id}` — Get transcript
- `GET /task-status/{id}` — Get task status
- `DELETE /evidence/{id}` — Delete evidence

#### User Routes (`/api/v1/users/*`)
- `GET /profile` — Get user profile
- `GET /cases` — List cases
- `POST /cases` — Create case (non-guest only)
- `GET /cases/{id}` — Get case details

---

## Token Validation Flow

### JWT Tokens (Regular Users)
```
Token Request
    ↓
Backend generates JWT with:
  - sub: user identifier
  - exp: expiration time
  - scopes: permissions
    ↓
Frontend stores in cookies + localStorage
    ↓
Frontend sends: Authorization: Bearer <jwt_token>
    ↓
Backend decode with SECRET_KEY
    ↓
Return UserContext(is_guest=False, ...)
```

### Guest Tokens (Demo Users)
```
POST /api/v1/auth/guest
    ↓
Backend creates JWT with:
  - sub: "Guest User" (or custom name)
  - exp: ~15 minutes from now
    ↓
Save to guest_tokens table:
  - token: (full JWT string)
  - name: (provided name)
  - is_active: true
  - expires_at: (timestamp)
    ↓
Return { access_token, saved: true }
    ↓
Frontend stores in cookies + localStorage
    ↓
Frontend sends: Authorization: Bearer <guest_token>
    ↓
Backend:
  1. Try JWT decode → SUCCESS
  2. Create UserContext(
       id=jti,
       name=payload.sub,
       is_guest=True,
       is_demo=True
     )
    ↓
Return UserContext → Route handler uses it
```

---

## Database Models

### GuestToken Table
```python
class GuestToken(Base):
    __tablename__ = "guest_tokens"
    
    id: UUID (primary key)
    name: str (optional, e.g., "Guest User")
    token: str (unique, the actual JWT)
    is_active: bool (default=True)
    created_at: datetime
    expires_at: datetime
```

### Relationships Used
- `Evidence` → Tracks uploaded files
- `Analysis` → Stores analysis results
- `TranscriptSegment` → Stores transcript data
- `ChainOfCustody` → Audit trail (who did what, when)

---

## Usage Examples

### Frontend: Get Token
```typescript
// frontend/app/login/page.tsx
const handleGuest = async () => {
  const res = await fetch("http://localhost:8000/api/v1/auth/guest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "Guest User" })
  });
  
  const data = await res.json();
  
  // Save token
  saveTokenToCookie(data.access_token, 15);  // 15 minutes
  saveTokenToStorage(data.access_token);
  
  // Navigate
  router.push("/");
};
```

### Frontend: Use Token in API Calls
```typescript
// frontend/lib/api.ts
export async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = getToken();
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${token}`
    }
  });
  
  return response;
}

// Usage
const evidence = await apiGet("/api/v1/forensics/evidence");
```

### Backend: Protected Route
```python
# backend/app/routers/forensics.py
@router.get("/evidence")
async def get_user_evidence(
    user: UserContext = Depends(get_current_user),  # ← Token validation
    db: Session = Depends(db_session.get_db)
):
    # At this point, 'user' is always valid
    # If token was invalid, get_current_user raises 401
    
    evidence_files = db.query(models.Evidence)\
        .order_by(models.Evidence.uploaded_at.desc())\
        .all()
    
    return [
        EvidenceOut(
            id=str(f.id),
            filename=f.filename,
            ...
        )
        for f in evidence_files
    ]
```

---

## Error Handling

### Invalid Token (401 Unauthorized)
```
Request:
  GET /api/v1/forensics/evidence
  Authorization: Bearer invalid_token_xyz

Response:
  HTTP 401
  {
    "detail": "Could not validate credentials"
  }
```

### Missing Token (401 Unauthorized)
```
Request:
  GET /api/v1/forensics/evidence
  (no Authorization header)

Response:
  HTTP 401
  {
    "detail": "Not authenticated"
  }
```

### Guest Action Restriction (403 Forbidden)
```
Request:
  POST /api/v1/users/cases
  Authorization: Bearer <guest_token>
  {"title": "New Case"}

Response:
  HTTP 403
  {
    "detail": "Guest users cannot create cases"
  }
```

### Resource Not Found (404)
```
Request:
  GET /api/v1/forensics/evidence/nonexistent-id
  Authorization: Bearer <valid_token>

Response:
  HTTP 404
  {
    "detail": "Evidence not found"
  }
```

---

## Security Considerations

### 1. Token Storage (Frontend)
✅ **Cookies:** HttpOnly, Secure, SameSite
✅ **localStorage:** Backup storage
❌ **Never:** Store in plain text

### 2. Token Transmission
✅ **HTTPS Only** (enforced in production)
✅ **Bearer token in Authorization header**
❌ **Never:** Pass token in URL or body

### 3. Token Validation (Backend)
✅ **Always decode with SECRET_KEY**
✅ **Check expiration**: `exp > datetime.utcnow()`
✅ **Check active flag**: `is_active == True`
❌ **Never:** Skip validation

### 4. Rate Limiting
✅ Guest users: 5MB file size limit
✅ Guest tokens: 15 minute expiration
✅ Log all access attempts

### 5. Audit Trail
✅ All actions logged in `chain_of_custody`
✅ Track: who, what, when
✅ Immutable records for legal compliance

---

## Configuration

### Environment Variables
```bash
# backend/.env
SECRET_KEY="<generated via openssl rand -hex 32>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440      # Regular users
DEMO_TOKEN_EXPIRE_MINUTES=15          # Guest users
```

### Startup Behavior
```python
# backend/app/main.py
@app.on_event("startup")
async def startup_migrations():
    """Auto-detect model changes and apply migrations."""
    auto_migrate_on_startup(skip_autogenerate=False)
```

---

## Testing

### Test Guest Flow
```bash
# 1. Get token (15 min expiry)
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/guest \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Guest"}' | jq -r '.access_token')

# 2. Use token
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN"

# 3. Token expires after 15 minutes
sleep 901  # Wait 15 min 1 sec
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN"
# → 401 Unauthorized
```

### Test Protected Route
```bash
# Without token
curl -X GET "http://localhost:8000/api/v1/forensics/evidence"
# → 401 Not authenticated

# With token
curl -X GET "http://localhost:8000/api/v1/forensics/evidence" \
  -H "Authorization: Bearer $TOKEN"
# → 200 OK (returns list of evidence)
```

---

## Next Steps

1. ✅ **Token generation** — `/api/v1/auth/guest`
2. ✅ **Token validation** — `get_current_user()`
3. ✅ **Protected routes** — All forensics/users routes
4. ⏳ **Token refresh** — Implement refresh tokens (optional)
5. ⏳ **Multi-factor auth** — Add if needed
6. ⏳ **API keys** — For third-party integrations

---

