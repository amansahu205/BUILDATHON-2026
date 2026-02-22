# Verdict Frontend API Integration Guide for Lovable

Please use this guide to connect the frontend UI to the FastAPI backend. You should update the API service files (e.g., `api.ts`, `auth.ts`, `cases.ts`, `sessions.ts`) to match these contracts exactly.

## Base URL
**Production Server:** `https://verdict-backend-production.up.railway.app/api/v1`

*Note: All endpoints below are relative to this Base URL.*

## Authentication
Most endpoints require a Bearer token. Send `Authorization: Bearer <accessToken>`.

---

## 1. Authentication (`/api/v1/auth`)

**Login**
* `POST /api/v1/auth/login`
* Request Body: `{ "email": "user@firm.com", "password": "password123" }`
* Response: `{ "success": true, "data": { "accessToken": "...", "refreshToken": "...", "user": { "id": "...", "email": "..." } } }`

---

## 2. Cases (`/api/v1/cases`)

**List Cases**
* `GET /api/v1/cases`
* Headers: `Authorization: Bearer <token>`
* Response: `{ "success": true, "data": [ { "id": "...", "name": "...", "depositionDate": "...", "caseType": "..." } ] }`

---

## 3. Sessions (`/api/v1/sessions`)

**Get Session Details**
* `GET /api/v1/sessions/:session_id`
* Response: `{ "success": true, "data": { "id": "...", "status": "ACTIVE", "startedAt": "..." } }`

**Start Session**
* `POST /api/v1/sessions/:session_id/start`
* Request: `{}`
* Response: `{ "success": true, "data": { "sessionId": "...", "status": "ACTIVE" } }`

**Generate Question (Interrogator Agent) [STREAMING]**
* `POST /api/v1/sessions/:session_id/agents/question`
* Content-Type: `application/json`
* Request Body: 
```json
{
  "questionNumber": 1,
  "currentTopic": "PRIOR_STATEMENTS",
  "priorAnswer": "I don't remember",
  "hesitationDetected": false,
  "recentInconsistencyFlag": false
}
```
* **IMPORTANT**: This endpoint returns an event stream (`text/event-stream`). You must parse Server-Sent Events (SSE). It emits JSON strings containing `{'type': 'QUESTION_CHUNK', 'text': '...'}` and finally `{'type': 'QUESTION_AUDIO', 'audioBase64': '...'}`.

**Check Objection (Objection Copilot)**
* `POST /api/v1/sessions/:session_id/agents/objection`
* Request Body: 
```json
{
  "questionNumber": 1,
  "questionText": "Isn't it true you were speeding?"
}
```
* Response: 
```json
{
  "success": true,
  "data": {
    "isObjectionable": true,
    "category": "LEADING",
    "freRule": "FRE 611",
    "explanation": "Leading question on direct examination",
    "confidence": 0.95
  }
}
```

**Check Inconsistency (Inconsistency Detector)**
* `POST /api/v1/sessions/:session_id/agents/inconsistency`
* Request Body: 
```json
{
  "questionNumber": 1,
  "questionText": "What color was the light?",
  "answerText": "It was green."
}
```
* Response: 
```json
{
  "success": true,
  "data": {
    "flagFound": true,
    "severity": "HIGH",
    "explanation": "Witness previously stated the light was red.",
    "sourceQuote": "The light was definitely red.",
    "documentId": "depo-123"
  }
}
```

Please update the frontend data fetching hooks (e.g. TanStack Query) to wire these up exactly as described.
