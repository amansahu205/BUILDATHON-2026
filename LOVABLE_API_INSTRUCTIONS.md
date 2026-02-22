# VERDICT — Lovable Frontend ↔ Backend Integration Guide

> **Deployed Backend:** `https://verdict-backend-production.up.railway.app`  
> **Deployed Frontend:** `https://verdict-io.lovable.app`  
> **Last updated:** Feb 22, 2026 — all field names reflect the live schema

---

## CRITICAL SETUP — DO THIS FIRST

Create (or update) the environment file so every API call points at the live backend:

```ts
// src/lib/api.ts  (or wherever your axios/fetch base is configured)
export const API_BASE = "https://verdict-backend-production.up.railway.app/api/v1";
```

All API paths below are **relative to `API_BASE`**. Every authenticated request must send:

```
Authorization: Bearer <accessToken>
```

The access token is returned by `/auth/login` — store it in `localStorage` or React context and attach it via an Axios request interceptor.

---

## AUTH HEADER HELPER (copy into `src/lib/api.ts`)

```ts
import axios from "axios";

export const api = axios.create({
  baseURL: "https://verdict-backend-production.up.railway.app/api/v1",
  withCredentials: true, // send httpOnly cookies for refresh
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

---

## 1. AUTHENTICATION  `/auth`

### POST `/auth/login`

```ts
// Request
{ email: string; password: string }

// Response 200
{
  success: true,
  data: {
    user: { id, firmId, email, name, role },
    tokens: { accessToken: string; refreshToken: string }
  }
}
```

> Store `accessToken` in `localStorage`. The backend also sets httpOnly cookies automatically.

**Demo credentials:** `sarah.chen@demo.com` / `Demo!Pass123`

---

### POST `/auth/refresh`

No body needed — reads the `refresh_token` httpOnly cookie.

```ts
// Response 200
{ success: true, data: { expiresAt: "2026-02-22T20:00:00Z" } }
```

---

### POST `/auth/logout`

No body. Clears cookies and revokes the refresh token.

```ts
// Response 200
{ success: true, message: "Logged out successfully" }
```

---

### GET `/auth/me`

```ts
// Response 200
{
  success: true,
  data: { id, firmId, email, name, role }
}
```

---

## 2. CASES  `/cases`

### GET `/cases`

List all non-archived cases for the authenticated user's firm.

```ts
// Response 200
{
  success: true,
  data: {
    cases: [
      {
        id: string,
        caseName: string,        // ← was "name" — use caseName everywhere
        caseType: string,        // "MEDICAL_MALPRACTICE" | "EMPLOYMENT_DISCRIMINATION" | "COMMERCIAL_DISPUTE" | "CONTRACT_BREACH" | "OTHER"
        opposingParty: string | null,  // ← was "opposingFirm"
        witnessName: string | null,
        witnessRole: string | null,
        aggressionLevel: string | null, // "Low" | "Medium" | "High"
        depositionDate: string | null,
        createdAt: string
      }
    ],
    pagination: { page: 1, limit: 20, total: number }
  }
}
```

---

### POST `/cases`

Create a new case. All fields with `?` are optional.

```ts
// Request body
{
  caseName: string,           // required
  caseType: string,           // required — one of the CaseType enum values
  caseTypeCustom?: string,    // only if caseType = "OTHER"
  opposingParty?: string,
  depositionDate?: string,    // ISO 8601 e.g. "2026-03-15T00:00:00"
  witnessName?: string,
  witnessRole?: string,
  aggressionLevel?: string,   // "Low" | "Medium" | "High"
  extractedFacts?: string,
  priorStatements?: string,
  exhibitList?: string,
  focusAreas?: string
}

// Response 201
{
  success: true,
  data: {
    id, caseName, caseType, opposingParty, witnessName,
    witnessRole, aggressionLevel, depositionDate, createdAt
  }
}
```

---

### GET `/cases/:caseId`

Full case detail including facts for the Fact Review page.

```ts
// Response 200
{
  success: true,
  data: {
    id, caseName, caseType, opposingParty, witnessName, witnessRole,
    aggressionLevel, depositionDate, extractedFacts, priorStatements,
    exhibitList, focusAreas, createdAt
  }
}
```

---

### PATCH `/cases/:caseId`

Partial update — only send fields you want to change.

```ts
// Request body (all optional)
{
  caseName?: string,
  depositionDate?: string,
  opposingParty?: string,
  witnessName?: string,
  witnessRole?: string,
  aggressionLevel?: string,
  extractedFacts?: string,
  priorStatements?: string,
  exhibitList?: string,
  focusAreas?: string
}

// Response 200
{ success: true, data: { id, caseName } }
```

---

### DELETE `/cases/:caseId`

Archives (soft-deletes) the case.

```ts
// Response 200
{ success: true, message: "Case archived" }
```

---

## 3. WITNESSES  `/cases/:caseId/witnesses`

### GET `/cases/:caseId/witnesses`

```ts
// Response 200
{
  success: true,
  data: {
    witnesses: [
      { id, caseId, name, role, sessionCount, latestScore, plateauDetected, createdAt }
    ]
  }
}
```

---

### POST `/cases/:caseId/witnesses`

```ts
// Request body
{ name: string; email: string; role: string }
// role: "DEFENDANT" | "PLAINTIFF" | "EXPERT" | "CORPORATE_REPRESENTATIVE" | "OTHER"

// Response 201
{ success: true, data: { id, caseId, name, role, sessionCount, latestScore, createdAt } }
```

---

### GET `/cases/:caseId/witnesses/:witnessId`

```ts
// Response 200
{ success: true, data: { id, caseId, name, role, sessionCount, latestScore, plateauDetected, createdAt } }
```

---

## 4. SESSIONS  `/sessions`

### POST `/sessions`

Create a session (puts it in `LOBBY` state, generates `witnessToken`).

```ts
// Request body
{
  caseId: string,
  witnessId: string,
  durationMinutes: number,          // e.g. 30
  focusAreas: string[],             // e.g. ["TIMELINE_CHRONOLOGY", "FINANCIAL_DETAILS"]
  aggression: string,               // "STANDARD" | "ELEVATED" | "HIGH_STAKES"
  objectionCopilotEnabled: boolean, // default true
  sentinelEnabled: boolean          // default false
}

// Response 201
{
  success: true,
  data: {
    id: string,
    sessionNumber: number,
    status: "LOBBY",
    witnessToken: string,   // 24-char token; append to witness session URL
    durationMinutes: number
  }
}
```

---

### GET `/sessions/:sessionId`

```ts
// Response 200
{
  success: true,
  data: {
    id, caseId, witnessId, status, sessionNumber, durationMinutes,
    focusAreas, aggression, objectionCopilotEnabled, sentinelEnabled,
    createdAt, startedAt, endedAt, questionCount
  }
}
```

---

### POST `/sessions/:sessionId/start`

Move session from `LOBBY` to `ACTIVE`.

```ts
// Response 200
{ success: true, data: { sessionId, status: "ACTIVE", startedAt } }
```

---

### POST `/sessions/:sessionId/pause`

```ts
// Response 200
{ success: true, data: { sessionId, status: "PAUSED" } }
```

---

### POST `/sessions/:sessionId/resume`

```ts
// Response 200
{ success: true, data: { sessionId, status: "ACTIVE" } }
```

---

### POST `/sessions/:sessionId/end`

Move session to `COMPLETE`. Required before triggering brief generation.

```ts
// Response 200
{ success: true, data: { sessionId, status: "COMPLETE", endedAt } }
```

---

### GET `/sessions/:sessionId/live-state`

Poll this every 3 seconds from `LiveSessionPage` to sync transcript and alerts.

```ts
// Response 200
{
  success: true,
  data: {
    status: "active" | "paused" | "lobby" | "complete",
    elapsedSeconds: number,
    totalSeconds: number,
    currentTopic: string,
    questionCount: number,
    transcript: [
      { id, speaker, text, timestamp, flagged }
    ],
    alerts: [
      {
        id, type, severity, timestamp, title, description,
        freRule, confidenceScore, priorQuote, priorSource,
        priorPageLine, status
      }
    ],
    witnessConnected: boolean,
    serviceStatus: { elevenlabs: boolean, nemotron: boolean }
  }
}
```

---

### POST `/sessions/:sessionId/agents/question`  (SSE STREAMING)

Generates the next Interrogator question. Returns `text/event-stream` — parse with fetch + ReadableStream.

```ts
// Request body
{
  questionNumber: number,
  currentTopic: string,        // "TIMELINE_CHRONOLOGY" | "FINANCIAL_DETAILS" | "COMMUNICATIONS" | "RELATIONSHIPS" | "ACTIONS_TAKEN" | "PRIOR_STATEMENTS"
  priorAnswer?: string,
  hesitationDetected: boolean,
  recentInconsistencyFlag: boolean
}

// SSE events emitted in order:
// data: {"type":"QUESTION_START","questionNumber":1}
// data: {"type":"QUESTION_CHUNK","text":"Doctor, can you describe..."}
// data: {"type":"QUESTION_CHUNK","text":" the exact dosage..."}
// data: {"type":"QUESTION_AUDIO","audioBase64":"..."}   // optional TTS audio
// data: {"type":"QUESTION_END","fullText":"Doctor, can you describe the exact dosage..."}
```

```ts
// Parsing pattern (React)
const response = await fetch(`${API_BASE}/sessions/${sessionId}/agents/question`, {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
  body: JSON.stringify({ questionNumber, currentTopic, priorAnswer, hesitationDetected, recentInconsistencyFlag }),
});
const reader = response.body!.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  for (const line of chunk.split("\n")) {
    if (line.startsWith("data: ")) {
      const event = JSON.parse(line.slice(6));
      // handle event.type: QUESTION_START | QUESTION_CHUNK | QUESTION_AUDIO | QUESTION_END
    }
  }
}
```

---

### POST `/sessions/:sessionId/agents/objection`

Run Objection Copilot on a question. Responds in under 1.5 seconds.

```ts
// Request body
{ questionNumber: number; questionText: string }

// Response 200
{
  success: true,
  data: {
    isObjectionable: boolean,
    category: "LEADING" | "HEARSAY" | "COMPOUND" | "ASSUMES_FACTS" | "SPECULATION" | null,
    freRule: string | null,       // e.g. "FRE 611(c)"
    explanation: string | null,
    confidence: number,           // 0.0 - 1.0
    processingMs: number
  }
}
```

---

### POST `/sessions/:sessionId/agents/inconsistency`

Run Inconsistency Detector on a witness answer. Responds in under 4 seconds.

```ts
// Request body
{ questionNumber: number; questionText: string; answerText: string }

// Response 200
{
  success: true,
  data: {
    flagFound: boolean,
    isLiveFired: boolean,          // true if confidence >= 0.75
    contradictionConfidence: number,
    priorQuote: string | null,
    priorDocumentPage: number | null,
    priorDocumentLine: number | null,
    impeachmentRisk: "STANDARD" | "HIGH"
  }
}
```

---

### POST `/sessions/:sessionId/answers/audio`

Submit witness audio for STT transcription (multipart form).

```ts
// Request: multipart/form-data
// Fields: file (audio Blob), questionNumber (int), durationMs (int, optional)

// Response 200
{
  success: true,
  data: { eventId, sessionId, questionNumber, transcriptText, audioS3Key, durationMs }
}
```

---

## 5. BRIEFS  `/briefs`

### POST `/briefs/generate/:sessionId`

Trigger brief generation (background task, takes 2-3 min).

```ts
// Response 200
{
  success: true,
  data: {
    briefId: string,
    status: "GENERATING" | "ALREADY_EXISTS",
    message: string
  }
}
```

---

### GET `/briefs/:briefId`

Poll after generation. Brief is ready when `narrativeText !== "Generating..."`.

```ts
// Response 200
{
  success: true,
  data: {
    id, sessionId, sessionScore, consistencyRate, deltaVsBaseline,
    confirmedFlags, objectionCount, composureAlerts,
    topRecommendations: string[],
    narrativeText: string,
    weaknessMapScores: {
      composure: number,
      tactical_discipline: number,
      professionalism: number,
      directness: number,
      consistency: number
    } | null,
    shareToken: string | null,
    pdfS3Key: string | null,
    createdAt: string
  }
}
```

---

### POST `/briefs/:briefId/share`

Generate a 7-day witness share link.

```ts
// Response 200
{ success: true, data: { shareToken: string; expiresAt: string; shareUrl: string } }
```

---

### GET `/briefs/share/:shareToken`  (NO AUTH REQUIRED)

Witness-safe read-only view.

```ts
// Response 200
{ success: true, data: { sessionScore, consistencyRate, topRecommendations, narrativeText } }
// 410 Gone if token expired
```

---

### GET `/briefs/:briefId/pdf`

Get a presigned S3 download URL.

```ts
// Response 200
{ success: true, data: { downloadUrl: string } }
```

---

## 6. DOCUMENTS  `/cases/:caseId/documents`

Three-step flow: request presigned URL, upload directly to S3, then confirm.

### Step 1 — POST `/cases/:caseId/documents/upload`

```ts
// Request body
{
  filename: string,
  mimeType: string,      // "application/pdf" | "application/vnd.openxmlformats-officedocument.wordprocessingml.document" | "text/plain"
  fileSizeBytes: number,
  docType?: string       // "PRIOR_DEPOSITION" | "MEDICAL_RECORDS" | "FINANCIAL_RECORDS" | "CORRESPONDENCE" | "EXHIBIT" | "OTHER"
}

// Response 200
{ success: true, data: { documentId: string; uploadUrl: string; s3Key: string } }
```

### Step 2 — PUT `uploadUrl` directly from the browser (bypass backend)

```ts
await fetch(uploadUrl, {
  method: "PUT",
  body: fileBlob,
  headers: { "Content-Type": mimeType },
});
```

### Step 3 — POST `/cases/:caseId/documents/:documentId/confirm`

```ts
// Response 200
{ success: true, data: { documentId, status: "UPLOADING", message: "Ingestion pipeline started." } }
```

### Poll — GET `/cases/:caseId/documents/:documentId/status`

```ts
// Response 200
{
  success: true,
  data: {
    status: "PENDING" | "UPLOADING" | "INDEXING" | "READY" | "FAILED",
    progress: number,   // 0-100
    pageCount?: number,
    error?: string
  }
}
```

---

## 7. HEALTH CHECK

```
GET https://verdict-backend-production.up.railway.app/api/v1/health
```

```ts
// Response 200
{ status: "ok", db: "connected", version: "1.0.0", timestamp: "..." }
```

---

## FIELD NAME REFERENCE — CASES

The Case schema was updated. Use these names or the backend returns 422 errors:

| Old (broken) | New (correct) |
|---|---|
| `name` | `caseName` |
| `opposingFirm` | `opposingParty` |
| *(missing)* | `witnessName` |
| *(missing)* | `witnessRole` |
| *(missing)* | `aggressionLevel` |

---

## ERROR RESPONSE SHAPE

```ts
{ detail: { code: string; message?: string } }
```

| HTTP | Code | Meaning |
|---|---|---|
| 401 | `INVALID_CREDENTIALS` | Wrong email or password |
| 401 | `TOKEN_INVALID` / `TOKEN_EXPIRED` | Re-authenticate |
| 403 | `ACCOUNT_INACTIVE` | User deactivated |
| 404 | `NOT_FOUND` | Resource missing or not in your firm |
| 400 | `INVALID_SESSION_STATUS` | Session in wrong state for that action |
| 400 | `FILE_TOO_LARGE` | Document over 200 MB |
| 400 | `UNSUPPORTED_FORMAT` | Not PDF, DOCX, or TXT |

---

## TANSTACK QUERY PATTERNS

```ts
// Cases list
const { data: cases } = useQuery({
  queryKey: ["cases"],
  queryFn: () => api.get("/cases").then(r => r.data.data.cases),
});

// Single case
const { data: caseDetail } = useQuery({
  queryKey: ["case", caseId],
  queryFn: () => api.get(`/cases/${caseId}`).then(r => r.data.data),
});

// Live session — poll every 3s
const { data: liveState } = useQuery({
  queryKey: ["live-state", sessionId],
  queryFn: () => api.get(`/sessions/${sessionId}/live-state`).then(r => r.data.data),
  refetchInterval: 3000,
  enabled: !!sessionId,
});

// Brief — poll until ready
const { data: brief } = useQuery({
  queryKey: ["brief", briefId],
  queryFn: () => api.get(`/briefs/${briefId}`).then(r => r.data.data),
  refetchInterval: (data) => data?.narrativeText === "Generating..." ? 5000 : false,
  enabled: !!briefId,
});

// Create case
const createCase = useMutation({
  mutationFn: (body: CreateCaseRequest) => api.post("/cases", body).then(r => r.data.data),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cases"] }),
});
```

---

## WEAKNESS MAP — RECHARTS RADAR CHART

```ts
const radarData = [
  { axis: "Composure",           score: brief.weaknessMapScores?.composure ?? 0 },
  { axis: "Tactical Discipline", score: brief.weaknessMapScores?.tactical_discipline ?? 0 },
  { axis: "Professionalism",     score: brief.weaknessMapScores?.professionalism ?? 0 },
  { axis: "Directness",          score: brief.weaknessMapScores?.directness ?? 0 },
  { axis: "Consistency",         score: brief.weaknessMapScores?.consistency ?? 0 },
];

<RadarChart data={radarData} cx={200} cy={200} outerRadius={150} width={400} height={400}>
  <PolarGrid />
  <PolarAngleAxis dataKey="axis" />
  <PolarRadiusAxis angle={30} domain={[0, 100]} />
  <Radar dataKey="score" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
</RadarChart>
```
