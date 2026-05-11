# VeriJust Backend API - Token-Protected Routes

## Overview

All protected routes require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

Tokens are obtained from either:
1. **Guest Access**: `POST /api/v1/auth/guest` (no auth required)
2. **Regular User**: Login with credentials (implement as needed)

---

## Authentication Routes

### POST `/api/v1/auth/guest`
Create a guest access token for demo/trial users.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/guest \
  -H "Content-Type: application/json" \
  -d '{"name": "Guest User"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "saved": true
}
```

**Token Validity:** 15 minutes (configurable via `DEMO_TOKEN_EXPIRE_MINUTES`)

---

## Forensics Routes (Protected)

### POST `/api/v1/forensics/upload`
Upload audio/video evidence for analysis.

**Protected:** ✅ Requires token
**Rate Limit:** Guest users limited to 5MB per file

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/forensics/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@evidence.mp3" \
  -F "case_id=c1234567-89ab-cdef-0123-456789abcdef"
```

**Response:**
```json
{
  "evidence_id": "e1234567-89ab-cdef-0123-456789abcdef",
  "task_id": "t1234567-89ab-cdef-0123-456789abcdef",
  "status": "processing",
  "message": "File 'evidence.mp3' uploaded. Analysis started."
}
```

---

### GET `/api/v1/forensics/evidence`
Get all evidence files (paginated).

**Protected:** ✅ Requires token

**Query Parameters:**
- `limit` (int, default 50, max 100)
- `offset` (int, default 0)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/forensics/evidence?limit=10&offset=0" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
[
  {
    "id": "e1234567-89ab-cdef-0123-456789abcdef",
    "filename": "evidence.mp3",
    "file_size_bytes": 1048576,
    "duration_seconds": 120.5,
    "mime_type": "audio/mpeg",
    "uploaded_at": "2026-02-23T10:30:00",
    "case_id": "c1234567-89ab-cdef-0123-456789abcdef"
  }
]
```

---

### GET `/api/v1/forensics/evidence/{evidence_id}`
Get details for a specific evidence file.

**Protected:** ✅ Requires token

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/forensics/evidence/e1234567-89ab-cdef-0123-456789abcdef" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": "e1234567-89ab-cdef-0123-456789abcdef",
  "filename": "evidence.mp3",
  "file_size_bytes": 1048576,
  "duration_seconds": 120.5,
  "mime_type": "audio/mpeg",
  "uploaded_at": "2026-02-23T10:30:00",
  "case_id": "c1234567-89ab-cdef-0123-456789abcdef"
}
```

---

### GET `/api/v1/forensics/analysis/{evidence_id}`
Get analysis results for evidence file.

**Protected:** ✅ Requires token

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/forensics/analysis/e1234567-89ab-cdef-0123-456789abcdef" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": "a1234567-89ab-cdef-0123-456789abcdef",
  "evidence_id": "e1234567-89ab-cdef-0123-456789abcdef",
  "status": "completed",
  "average_bluff_score": 0.72,
  "sentiment_distribution": {
    "angry": 0.2,
    "nervous": 0.4,
    "neutral": 0.4
  },
  "speaker_count": 2,
  "created_at": "2026-02-23T10:31:00",
  "completed_at": "2026-02-23T10:35:00"
}
```

---

### GET `/api/v1/forensics/transcript/{evidence_id}`
Get full transcript with segment analysis.

**Protected:** ✅ Requires token

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/forensics/transcript/e1234567-89ab-cdef-0123-456789abcdef" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "evidence_id": "e1234567-89ab-cdef-0123-456789abcdef",
  "segment_count": 5,
  "segments": [
    {
      "id": 1,
      "start_time": 0.0,
      "end_time": 2.5,
      "speaker_label": "Speaker 1",
      "text_content": "Hello, how are you today?",
      "is_bluff": false,
      "bluff_confidence": 0.15,
      "sentiment": "neutral"
    },
    {
      "id": 2,
      "start_time": 2.5,
      "end_time": 5.8,
      "speaker_label": "Speaker 2",
      "text_content": "I'm doing great, thanks for asking.",
      "is_bluff": true,
      "bluff_confidence": 0.85,
      "sentiment": "nervous"
    }
  ]
}
```

---

### GET `/api/v1/forensics/task-status/{task_id}`
Get Celery task status for ongoing analysis.

**Protected:** ✅ Requires token

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/forensics/task-status/t1234567-89ab-cdef-0123-456789abcdef" \
  -H "Authorization: Bearer <token>"
```

**Response (In Progress):**
```json
{
  "task_id": "t1234567-89ab-cdef-0123-456789abcdef",
  "status": "started",
  "progress": "AI is analyzing..."
}
```

**Response (Completed):**
```json
{
  "task_id": "t1234567-89ab-cdef-0123-456789abcdef",
  "status": "completed",
  "result": { "analysis_data": "..." }
}
```

---

### DELETE `/api/v1/forensics/evidence/{evidence_id}`
Delete evidence file and associated analysis.

**Protected:** ✅ Requires token
**Note:** Logs deletion in chain_of_custody for audit trail

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/forensics/evidence/e1234567-89ab-cdef-0123-456789abcdef" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "message": "Evidence 'evidence.mp3' deleted successfully",
  "evidence_id": "e1234567-89ab-cdef-0123-456789abcdef"
}
```

---

## User Routes (Protected)

### GET `/api/v1/users/profile`
Get authenticated user's profile.

**Protected:** ✅ Requires token

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": "u1234567-89ab-cdef-0123-456789abcdef",
  "name": "Guest",
  "full_name": "Guest User",
  "email": null,
  "is_guest": true,
  "organization_name": null,
  "tier": "guest",
  "is_active": true,
  "created_at": "2026-02-23T10:30:00"
}
```

---

### GET `/api/v1/users/cases`
Get all cases for authenticated user.

**Protected:** ✅ Requires token

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/cases" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
[
  {
    "id": "c1234567-89ab-cdef-0123-456789abcdef",
    "title": "Case #2026-001",
    "description": "Evidence from incident",
    "client_name": "Law Enforcement",
    "case_number": "CASE-2026-001",
    "status": "open",
    "created_at": "2026-02-23T10:30:00"
  }
]
```

---

### POST `/api/v1/users/cases`
Create a new case.

**Protected:** ✅ Requires token
**Restriction:** Guest users cannot create cases

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/users/cases" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Case #2026-002",
    "description": "Evidence from incident",
    "client_name": "Law Enforcement",
    "case_number": "CASE-2026-002"
  }'
```

**Response:**
```json
{
  "id": "c1234567-89ab-cdef-0123-456789abcdef",
  "title": "Case #2026-002",
  "description": "Evidence from incident",
  "client_name": "Law Enforcement",
  "case_number": "CASE-2026-002",
  "status": "open",
  "created_at": "2026-02-23T10:30:00"
}
```

---

### GET `/api/v1/users/cases/{case_id}`
Get case details by ID.

**Protected:** ✅ Requires token

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/cases/c1234567-89ab-cdef-0123-456789abcdef" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "id": "c1234567-89ab-cdef-0123-456789abcdef",
  "title": "Case #2026-001",
  "description": "Evidence from incident",
  "client_name": "Law Enforcement",
  "case_number": "CASE-2026-001",
  "status": "open",
  "created_at": "2026-02-23T10:30:00"
}
```

---

## Error Handling

All protected routes return `401 Unauthorized` if token is missing or invalid:

```json
{
  "detail": "Could not validate credentials"
}
```

Common HTTP Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

---

## Token Flow Diagram

```
┌─────────────────────────────────────────┐
│  Frontend (Next.js)                     │
└────────────┬────────────────────────────┘
             │
             │ 1. POST /api/v1/auth/guest
             │    (no auth required)
             ▼
┌─────────────────────────────────────────┐
│  Backend (FastAPI)                      │
│  ┌───────────────────────────────────┐  │
│  │ Auth Router                       │  │
│  │ - Create guest token              │  │
│  │ - Save to Supabase                │  │
│  │ - Return { access_token, saved }  │  │
│  └───────────────────────────────────┘  │
└────────────┬────────────────────────────┘
             │
             │ 2. Return token to frontend
             ▼
┌─────────────────────────────────────────┐
│  Frontend (Next.js)                     │
│  - Save token to cookies                │
│  - Save token to localStorage           │
│  - Store in AuthContext                 │
└────────────┬────────────────────────────┘
             │
             │ 3. GET /api/v1/forensics/evidence
             │    Authorization: Bearer <token>
             ▼
┌─────────────────────────────────────────┐
│  Backend (FastAPI)                      │
│  ┌───────────────────────────────────┐  │
│  │ Dependencies (get_current_user)   │  │
│  │ - Decode JWT or lookup guest      │  │
│  │ - Return UserContext              │  │
│  ├───────────────────────────────────┤  │
│  │ Protected Routes                  │  │
│  │ - Use user context for queries    │  │
│  │ - Return data                     │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Testing the API

### 1. Get Guest Token
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/guest \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Guest"}' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Test Protected Route
```bash
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Upload Evidence
```bash
curl -X POST "http://localhost:8000/api/v1/forensics/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/evidence.mp3"
```

---

## Implementation Notes

- **Token Storage:** Persisted to `guest_tokens` table in Supabase
- **Token Validation:** JWT decode + database lookup for guest tokens
- **Rate Limiting:** Demo/guest users limited to 5MB file uploads
- **Chain of Custody:** All actions logged for audit trail
- **Error Logging:** All endpoint errors logged with full stack trace

