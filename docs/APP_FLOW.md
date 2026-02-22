# APP_FLOW.md — VERDICT
> AI-Powered Deposition Coaching & Trial Preparation Platform  
> Version: 1.0.0 — Hackathon Edition | February 21, 2026  
> Track: AI Automation — August.law Sponsor Track | Team: VoiceFlow Intelligence
<!-- Updated: Feb 22 2026 — Nia removed, Databricks Vector Search added, voiceagents integrated -->

---

## TABLE OF CONTENTS

1. [Entry Points](#1-entry-points)
2. [Core User Flows](#2-core-user-flows)
3. [Navigation Map](#3-navigation-map)
4. [Screen Inventory](#4-screen-inventory)
5. [Decision Points](#5-decision-points)
6. [Error Handling](#6-error-handling)
7. [Responsive Behavior](#7-responsive-behavior)
8. [Animations & Transitions](#8-animations--transitions)

---

## 1. ENTRY POINTS

### 1.1 Primary Entry Points (B2B — Law Firm Context Only)

| URL | Target Screen | Auth Required | Intended User |
|-----|--------------|---------------|---------------|
| `verdict.law/` | B2B Marketing Landing | No | Law firm decision-makers |
| `verdict.law/login` | Login Page | No | All firm users |
| `verdict.law/dashboard` | Attorney Dashboard | Yes | Partners, Associates |
| `verdict.law/cases` | Case List | Yes | All authenticated users |
| `verdict.law/cases/:caseId` | Case Detail | Yes | Case owner + authorized firm members |
| `verdict.law/cases/:caseId/session/new` | New Session Setup | Yes | Attorney running prep |
| `verdict.law/cases/:caseId/session/:sessionId/live` | Live Session | Yes | Attorney view |
| `verdict.law/cases/:caseId/witnesses/:witnessId` | Witness Profile | Yes | Attorney only |
| `verdict.law/witness/session/:sessionId` | Witness Session | Token only | Witness (no login) |
| `verdict.law/briefs/:briefId` | Coaching Brief | Yes or share token | Attorney + witness |
| `verdict.law/admin` | Firm Admin Panel | Yes — Admin role | Firm IT / Managing Partner |

### 1.2 Deep Links (Email Notifications)

```
Brief Ready Email:
  URL: verdict.law/briefs/:briefId?token=:secureToken
  Behavior: Token validates → Brief Viewer
  Token TTL: 7 days, single-device
  Expired: "This link has expired. Contact your attorney for a new one."

Witness Practice Invitation:
  URL: verdict.law/witness/session/:sessionId?token=:witnessToken
  Behavior: No login required; token-gated witness session entry
  Token TTL: 72 hours; invalidated when session starts

Score Plateau Alert:
  URL: verdict.law/cases/:caseId/witnesses/:witnessId?alert=plateau
  Behavior: Auth → Witness Profile with plateau banner expanded
  Recipient: Owning attorney only

Ingestion Complete:
  URL: verdict.law/cases/:caseId?tab=documents&status=ready
  Behavior: Auth → Case Detail, Documents tab, newly-indexed docs highlighted
```

### 1.3 Authentication Methods

| Method | Flow | Use Case |
|--------|------|----------|
| Firm SSO (SAML 2.0 / Okta) | Enterprise IdP redirect | AmLaw 200, iManage firms |
| Email + Password | Standard login form | Pilot firms without SSO |
| Magic Link (witness only) | Tokenized URL, no account | Witness access — no firm login required |

> **No OAuth social login (Google, Apple).** Enterprise legal tool — firm IT controls identity.  
> **No consumer signup flow.** VERDICT is sold to law firms, not individual users.

### 1.4 No Public SEO / Consumer Entry Points

VERDICT is a B2B SaaS product. There are no public content pages, guide pages, TikTok UTM flows, or consumer landing pages inside the application. All unauthenticated non-marketing traffic routes to `/login`. The marketing site is a separate domain (`trueverdict.com`) and is out of scope for this document.

---

## 2. CORE USER FLOWS

---

### FLOW 2.1 — Firm Onboarding & Account Setup (Admin — One-Time)

#### HAPPY PATH

```
Step 1: Firm Activation Email
├── VERDICT sales team sends invitation: [ACTIVATE YOUR FIRM ACCOUNT]
├── URL: verdict.law/onboarding?token=:firmToken  (TTL: 72 hours)
└── Next: Firm Configuration

Step 2: Firm Configuration → /onboarding
├── UI: Progress bar "Step 1 of 3"
├── Fields:
│   ├── Firm Name (pre-populated from contract)
│   ├── Primary Admin Name + Email (pre-populated)
│   ├── Seat count displayed: "Your plan: 25 seats"
│   └── SSO toggle: [Configure Okta/SAML] OR [Use Email/Password]
│
├── Path A — SSO:
│   ├── Admin provides SAML Metadata URL or XML upload
│   ├── VERDICT validates SAML handshake
│   └── "✅ SSO configured — users at your domain auto-provisioned"
│
└── Path B — Email/Password:
    ├── Admin sets password policy (min length, expiry days)
    └── Next: Seat Provisioning

Step 3: Seat Provisioning → /onboarding/users
├── UI: Progress bar "Step 2 of 3"
├── Options:
│   ├── [Upload CSV] — columns: Name, Email, Role
│   └── Manual add: Name + Email + Role dropdown
│       └── Roles: Partner / Associate / Paralegal / Admin
├── [INVITE ALL] → sends onboarding emails to all provisioned users
└── Next: Security Settings

Step 4: Security Settings → /onboarding/security
├── UI: Progress bar "Step 3 of 3"
├── Settings:
│   ├── Data retention: 30 / 60 / 90 days (default: 90)
│   ├── Case isolation: shown as read-only confirmation
│   └── Behavioral Sentinel: firm-level ON/OFF (default: OFF)
├── [COMPLETE SETUP] → firm record created in Databricks Delta Lake
└── Redirect: /admin

Step 5: Admin Dashboard → /admin
├── Displays: Seats used, pending invitations, security settings
└── Firm is fully provisioned; attorneys can create cases
```

#### ERROR STATES — Firm Onboarding

| Error | Display | Recovery |
|-------|---------|----------|
| Token expired | "This setup link has expired. Contact support@verdict.law" | Sales re-sends; no self-service |
| SSO metadata invalid | "Could not parse SAML metadata. Re-upload XML or check URL." | Retry |
| CSV format error | "Row 12: Missing email. Download corrected template." | Highlight bad rows, re-upload |
| Seat limit exceeded | "27 users added, plan includes 25 seats. [Upgrade] or reduce list." | Remove excess or upgrade |

---

### FLOW 2.2 — Case Creation & Document Ingestion (P0.4)

#### HAPPY PATH

```
Step 1: New Case → /cases/new
├── UI Elements:
│   ├── Case Name (e.g., "Chen v. Metropolitan Hospital")
│   ├── Case Type dropdown:
│   │   ├── Medical Malpractice
│   │   ├── Employment Discrimination
│   │   ├── Commercial Dispute
│   │   ├── Contract Breach
│   │   └── Other (free text)
│   ├── Opposing Firm (optional)
│   └── Deposition Date (date picker — drives dashboard countdown)
│
├── Validation: Case Name required (3–120 chars); Case Type required
├── System: POST /api/cases → case record created, empty document vault + witness list
└── Redirect: /cases/:caseId (Documents tab)

Step 2: Document Upload → /cases/:caseId (Documents tab)
├── UI Elements:
│   ├── Drag-and-drop zone (or [BROWSE FILES]):
│   │   ├── Accepted: PDF, DOCX, TXT
│   │   ├── Max per file: 200MB
│   │   └── Max per case: 2GB
│   ├── Helper text: "Upload prior depositions, medical records, contracts, exhibits"
│   ├── Document type tags (applied after upload):
│   │   ├── Prior Deposition (auto-detected by filename keywords)
│   │   ├── Medical Records / Financial Records / Correspondence / Exhibit
│   └── Document list (empty state: "No documents yet")
│
├── User: Drops files into upload zone
├── System: Files upload with per-file progress bars (% complete)
├── System: On upload complete → auto-triggers ingestion pipeline
└── Next: Ingestion Progress View (same screen, live status)

Step 3: Document Ingestion (live on Documents tab)
├── Per-document status cards:
│   ├── 🔵 Uploading: [████░░░░] 67%
│   ├── 🟡 Indexing: "Extracting facts... 127/250 pages"
│   ├── ✅ Ready: "Indexed — 23 key dates, 8 parties, 4 disputed facts"
│   └── 🔴 Failed: "Ingestion failed — [Retry] [View Error]"
├── Overall: "2 of 3 documents ready" header
├── [REVIEW EXTRACTED FACTS] button (active when ≥1 doc ready)
├── ETA shown: "~1m 45s remaining"
│
├── Document Upload Flow:
│   ├── Upload PDF/DOCX → S3 presigned PUT URL → confirm upload
│   ├── text extraction (pdfplumber for PDF / python-docx for DOCX)
│   ├── Claude fact extraction (parties, dates, disputedFacts, priorStatements)
│   ├── get_embedding() [Databricks gte-large-en, 1024d]
│   ├── upsert_prior_statement() [Databricks prior_statements_index, filtered by case_id]
│   └── Status: PENDING → UPLOADING → INDEXING → READY
│
└── System: In-app notification + email when all docs ingested

Step 4: Fact Review → /cases/:caseId/documents/facts
├── UI Elements:
│   ├── Parties — table with name + role; [Edit] inline
│   ├── Key Dates — table with date, event, source doc + page; [Edit] inline
│   ├── Disputed Facts — highlighted list; [Edit] per item
│   ├── Prior Sworn Statements — searchable index with page/line refs
│   ├── [ADD FACT] — manual entry for any section
│   ├── [Mark as Confirmed] checkbox per section
│   └── [CASE IS READY — ADD WITNESS] CTA (active when all sections confirmed)
│
├── User: Reviews facts, corrects errors, confirms sections
├── System: Saves corrections to Databricks Vector Search index (improves retrieval accuracy)
└── Success: All sections confirmed → attorney proceeds to add witness
```

#### ERROR STATES — Document Ingestion

| Error | Trigger | Display | Recovery |
|-------|---------|---------|----------|
| File too large | Upload > 200MB | "File is 312MB — max is 200MB. [Split document guide]" | Re-upload split version |
| Unsupported format | .DOC, scanned image PDF | "Scanned/image PDFs not supported in v1.0. Use text-searchable PDFs." | Re-upload correct version |
| Ingestion timeout | Ingestion pipeline > 5 minutes | "Taking longer than expected. [Proceed with partial index] [Keep waiting]" | Partial or retry |
| Zero text extracted | Blank/corrupted PDF | "No text content found. PDF may be image-only." | Re-upload text-searchable version |
| Storage limit | Case total > 2GB | "Case storage limit reached. Remove old docs or contact support." | Delete docs or upgrade |

#### EDGE CASES — Document Ingestion

- **Duplicate upload:** Backend detects identical file hash (SHA-256) → "This document looks identical to [filename]. Add anyway?"
- **Session configured before ingestion completes:** [Start Session] disabled with tooltip: "Waiting for document indexing to finish."
- **Browser closed mid-upload:** Upload state stored server-side; attorney returns to exact progress on next visit.
- **Re-upload of modified doc:** Replaces prior version; re-upserts to Databricks Vector Search; prior session references preserved with version tag.

---

### FLOW 2.3 — Witness Setup & Session Configuration

#### HAPPY PATH

```
Step 1: Add Witness → /cases/:caseId (Witnesses tab)
├── [+ ADD WITNESS] → modal overlay
├── Witness form:
│   ├── Full Name (required)
│   ├── Role: Defendant / Plaintiff / Expert / Corporate Representative / Other
│   ├── Email (required — for practice link delivery)
│   ├── Link to uploaded docs: checkboxes (which prior deposition belongs to this witness)
│   └── Notes (free text — e.g., "Known weakness: medication dosage timeline")
├── [SAVE WITNESS]
├── System: Creates Witness Profile, initializes empty score history
└── Witness card appears with [CONFIGURE SESSION] button active

Step 2: Session Configuration → /cases/:caseId/witnesses/:witnessId/session/new
├── UI Elements:
│   ├── Witness summary: Name, Role, Deposition countdown badge
│   ├── Prior sessions (if any): "Session 1 — Score: 58/100 — [View Brief]"
│   │
│   ├── SESSION SETTINGS:
│   │   ├── Duration: 15 / 30 / 45 / 60 min
│   │   ├── Focus Areas (multi-select chips):
│   │   │   ├── Timeline & Chronology
│   │   │   ├── Financial Details
│   │   │   ├── Communications & Correspondence
│   │   │   ├── Relationships & Key Parties
│   │   │   ├── Actions Taken
│   │   │   └── Prior Sworn Statements
│   │   ├── Interrogator Aggression:
│   │   │   ├── Standard (default)
│   │   │   ├── Elevated (more follow-up pressure)
│   │   │   └── High-Stakes (deposition-eve intensity)
│   │   ├── Objection Copilot: ON/OFF (default: ON)
│   │   └── Behavioral Sentinel: ON/OFF (shown only if firm-level enabled; default: OFF)
│   │
│   ├── [GENERATE PRACTICE LINK] → creates time-limited witness token URL
│   └── [START SESSION AS ATTORNEY] → attorney solo mode → /session/:id/lobby
│
├── System: POST /api/sessions → session record created
│   ├── build_system_prompt(case)            [uses extracted_facts, prior_statements, exhibit_list, focus_areas]
│   ├── get_conversation_token(agent_id)     [ElevenLabs signed WebSocket URL]
│   └── build_conversation_override(...)     [per-session ElevenLabs Conversational AI config]
├── System: Pre-briefs Interrogator Agent with:
│   ├── Case type, witness role, configured focus areas
│   ├── Prior session weak areas (Session 2+ only)
│   └── Indexed prior sworn statements from Databricks Vector Search
└── Next: Session Lobby
```

#### ERROR STATES — Session Configuration

| Error | Display | Recovery |
|-------|---------|----------|
| No documents indexed | Warning: "Inconsistency Detector cannot run without indexed prior statements. [Upload documents first]" | Proceed without detection OR upload first |
| Witness email invalid | Inline: "Please enter a valid email address" | Re-enter |
| Session already active for witness | "This witness has an active session in progress. [View it] or wait for completion." | View or wait |

---

### FLOW 2.4 — Live Deposition Simulation (P0.1 + P0.2 + P0.3 + P1.4)

#### HAPPY PATH — SESSION LOBBY

```
Session Lobby → /cases/:caseId/session/:sessionId/lobby
├── UI Elements:
│   ├── Session brief (read-only):
│   │   ├── Witness: Dr. Emily Chen | Defendant Physician
│   │   ├── Case: Chen v. Metropolitan Hospital | Medical Malpractice
│   │   ├── Duration: 45 min | Focus: Medication Dosage, Consultation Protocols
│   │   ├── Documents indexed: 3 (250 pages of prior testimony)
│   │   └── Prior sessions: Session 1 — 58/100
│   ├── Witness connection status: "Waiting for witness to join..."
│   │   └── [COPY LINK] [RESEND EMAIL] buttons
│   ├── Feature toggle review (read-only confirmation):
│   │   ├── Objection Copilot: ● ON
│   │   ├── Inconsistency Detector: ● ON (Nemotron)
│   │   └── Behavioral Sentinel: ○ OFF (or ● ON if configured)
│   └── [BEGIN SESSION WITHOUT WITNESS] — attorney solo mode
│
├── Witness joins via their link → "✅ Witness connected — Dr. Chen"
├── Attorney clicks [BEGIN SESSION]
└── Next: Live Session — Attorney View
```

#### HAPPY PATH — ACTIVE SESSION (ATTORNEY VIEW)

```
Active Session → /cases/:caseId/session/:sessionId/live

THREE-PANEL LAYOUT:

LEFT PANEL — Session Control (220px, fixed)
├── Timer: 23:14 remaining (amber < 10 min, red < 5 min)
├── Current topic: "Medication Dosage Timeline"
├── Question: Q7 of ~18 estimated
├── [⏸ PAUSE SESSION]
├── [⏭ SKIP TO NEXT TOPIC]
└── [⏹ END SESSION EARLY]

CENTER PANEL — Live Transcript (flexible width)
├── Speaker-tagged transcript, auto-scrolling:
│   ├── [INTERROGATOR Q7 — 00:14:22]: "Isn't it true you ordered the medication..."
│   └── [WITNESS — 00:14:38]: "I always consult before adjusting doses, approximately..."
├── Flagged exchange: red left-border highlight
└── [📋 Export Transcript] button (top-right, active on session end)

RIGHT PANEL — Live Alerts Rail (320px, fixed)
├── OBJECTION COPILOT ALERTS (fires ≤ 1.5s after question delivery):
│   └── 🔴 LEADING — FRE 611(c) | Q7 | 00:14:22
│       "Question suggests a specific answer. Witness should pause before answering."
│       [Mark Coached] [Dismiss]
│
├── INCONSISTENCY DETECTOR ALERTS (fires ≤ 4s after answer):
│   └── 🔴 CONTRADICTION | Q8 | 00:15:03 | Confidence: 0.91
│       Prior: "The dosage was exactly $217." — p.47, line 12
│       Now: "approximately $200 range"
│       [✓ Confirm] [✗ Reject] [📝 Annotate]
│
├── BEHAVIORAL SENTINEL ALERTS (if enabled — fires ≤ 2s):
│   └── 🟠 COMPOSURE ALERT | Q8 | 00:15:01 | 🧪 Experimental
│       "Fear micro-expression (AU4+AU20) 1.2s — gaze aversion detected"
│       "Inconsistency flag upgraded: HIGH IMPEACHMENT RISK"
│       [Noted] [Disable for session]
│
└── ALERT LOG scrolls newest-first; timestamp + Q-number on each alert

BOTTOM BAR:
└── [📝 ADD NOTE] — timestamped free-text annotation to current exchange
```

#### HAPPY PATH — WITNESS VIEW

```
Witness Session → /witness/session/:sessionId (token-gated, no firm login)

MINIMAL SINGLE-PANEL:
├── "Opposing Counsel" avatar (centered)
├── ElevenLabs waveform visualizer (when question is playing)
├── "Your Turn" mic indicator (after question ends)
├── Session timer (counts down — visible to witness)
└── [Need a Moment] button — pauses session, notifies attorney

NOT SHOWN TO WITNESS:
├── Alert rail — witness does NOT see inconsistency or objection flags
├── Live transcript — prevents real-time self-coaching
├── Score or any performance indicator during session
└── Attorney annotations

Session complete (witness side): "Session complete. Your attorney will be in touch."
```

#### INTERROGATOR AGENT LOGIC (P0.1)

```
On session start:
├── Reads: case type, witness role, focus areas, prior weak areas (Session 2+)
├── search_prior_statements() via Databricks Vector Search: retrieves relevant prior sworn statements for context
└── Initializes question strategy for case type

Adaptive behavior during session:
├── Standard: Open → specific → challenge (per topic arc)
├── Hesitation escalation: IF witness silence > 4s
│   └── THEN: sharper follow-up — "Let me ask that differently, Doctor..."
├── Behavioral signal (if Sentinel active): IF Fear/Contempt detected for ≥0.8s
│   └── THEN: selects from high-pressure follow-up bank for current topic
└── Inconsistency co-occurrence: IF Detector fires on current topic
    └── THEN: Interrogator extends questioning on that topic before moving on

Delivery:
├── ElevenLabs TTS: "Opposing counsel" voice profile — authoritative, measured
├── Latency target: < 2s from question generation to audio start
└── Post-question: 4-second silence window before hesitation trigger activates
```

#### OBJECTION COPILOT LOGIC (P0.2)

```
Per question — fires in parallel with delivery (≤ 1.5s):
├── get_embedding(question_text) [Databricks gte-large-en]
├── search_fre_rules(top_k=3, deposition_only=True) [Databricks fre_rules_index]
├── Top 3 FRE rules + Advisory Committee Notes → Claude classification
├── { isObjectionable, freRule, category, confidence } in ≤1.5s
├── Classifies:
│   ├── Leading (FRE 611c): suggests specific answer
│   ├── Hearsay (FRE 801): out-of-court statement for truth of matter asserted
│   ├── Compound: multiple questions embedded in one
│   ├── Assumes Facts Not in Evidence: presupposes unestablished facts
│   └── Calls for Speculation: asks witness to guess beyond their knowledge
│
├── IF objectionable:
│   ├── Alert fires in rail with FRE rule number + plain-English explanation
│   ├── Optional soft audio chime to attorney (configurable)
│   └── Event logged: question ID, timestamp, type, FRE rule
│
└── IF not objectionable: silent pass — no UI noise
```

#### INCONSISTENCY DETECTOR LOGIC (P0.3)

```
Per witness answer — fires ≤ 4s after answer:
├── Answer → Claude extracts key claims, facts, numerical values
├── get_embedding(witness_answer) [Databricks gte-large-en, 1024d]
├── search_prior_statements(case_id, answer, top_k=3) [Databricks prior_statements_index]
├── Top 3 semantically similar prior statements → Nemotron contradiction scoring
├── If confidence ≥ 0.75: INCONSISTENCY alert → WebSocket to attorney
│
├── Nemotron output: { contradiction_confidence: float, prior_quote, page, line }
│
├── IF confidence ≥ 0.75:
│   ├── Check Behavioral Sentinel co-occurrence:
│   │   ├── IF Fear or Contempt detected during same answer:
│   │   │   └── flag.risk = "HIGH IMPEACHMENT RISK" — confidence += 0.05
│   │   └── ELSE: flag.risk = "CONTRADICTION"
│   ├── Alert fires in live rail with prior quote + page/line + confidence
│   └── Attorney: [Confirm] [Reject] [Annotate]
│
├── IF confidence 0.50–0.74:
│   └── Queued in secondary_review — surfaced in brief, NOT in live rail
│
└── IF confidence < 0.50: silently discarded
```

#### ERROR STATES — Live Session

| Error | Trigger | Display | Recovery |
|-------|---------|---------|----------|
| ElevenLabs TTS down | Synthesis API failure | Banner: "Audio paused — questions displayed as text" | Text-only mode, session continues |
| ElevenLabs STT down | Transcription failure | Banner: "Voice recognition in fallback mode — accuracy reduced" | Browser Web Speech API fallback |
| Both TTS + STT down | Full ElevenLabs outage | Banner: "Text-only mode active" | Attorney types questions; witness types answers |
| Nemotron unavailable | API error / rate limit | Rail badge: "⚠️ Scoring: Claude-only mode (threshold raised to 0.85)" | Claude fallback, session continues |
| Databricks Vector Search unavailable | Service down | Rail badge: "FRE corpus offline — Objection Copilot running Claude-only" | Claude handles objections without FRE context |
| Witness disconnects | WebSocket drop | Attorney: "⚠️ Witness disconnected at Q12 — session paused" | Witness reconnects via same link; resumes from last complete exchange |
| Attorney disconnects | Browser close | Session state preserved; events buffered server-side | Reopen browser → session restores; Interrogator may continue if witness connected |
| Camera denied (Sentinel) | Witness refuses permission | Silent degradation | Attorney notified: "Behavioral Sentinel inactive — camera access not granted" |

#### EDGE CASES — Live Session

- **Attorney confirms then un-confirms a flag:** Re-opens the flag for re-review; brief reflects final state.
- **Zero inconsistencies all session:** Brief reads "No contradictions detected against uploaded prior statements" — not a blank.
- **Witness uses [Need a Moment]:** Interrogator pauses, timer pauses, attorney sees "Witness requested a break at Q12."
- **Two witnesses, same case, concurrent sessions:** Fully isolated — separate session IDs, event streams, alert rails.
- **Objection Copilot fires on every question:** Attorney can toggle it OFF mid-session from rail header; prior alerts preserved in log.
- **Interrogator would repeat a question:** Claude monitors prior context; prevents exact repeats; may rephrase within same topic.

---

### FLOW 2.5 — Coaching Brief Review (P0.5)

#### HAPPY PATH

```
Brief Generation → triggered when session ends
├── Review Orchestrator pipeline (target: ≤ 3 minutes):
│   ├── Collects all confirmed flags, objection events, attorney annotations
│   ├── Computes: session score (0–100), topic sub-scores, delta vs. Session 1
│   ├── Synthesizes: top 3 coaching recommendations
│   ├── generate_rule_based_report(transcript, events, case)
│   ├── Claude narrative synthesis (coaching brief text)
│   ├── ElevenLabs TTS Rachel voice (narrates flagged moments)
│   ├── PDF generation (matplotlib radar chart + reportlab)
│   └── Brief saved to PostgreSQL → brief_id returned

Brief Viewer → /briefs/:briefId

SCORE SUMMARY CARD:
├── Session Score: 58/100
│   └── Color-coded: red < 50 / amber 50–74 / green 75+
├── Delta vs. Session 1: Δ +17 (multi-session) or "First session baseline"
├── Consistency Rate: 73%
└── Alert totals: Objections fired: 4 | Confirmed inconsistencies: 3 | Composure alerts: 2

INCONSISTENCIES SECTION:
├── Each confirmed flag (expanded by default):
│   ├── Exchange timestamp + [▶ Play clip] (ElevenLabs audio)
│   ├── Current answer with problematic phrase highlighted
│   ├── Prior statement: exact quote + p.XX, line YY
│   ├── Contradiction confidence: 0.91
│   ├── Impeachment risk badge: HIGH (if Sentinel corroborated)
│   └── Coach note: "Witness should address the $217 figure proactively"
└── Secondary queue (0.50–0.74 confidence): collapsed, expandable, labeled "Possible Inconsistencies — Attorney Review"

OBJECTIONS SECTION:
├── Each event: timestamp, question text, FRE rule, classification
├── Training note: "Witness answered Q7 before pausing — coach to wait 3 seconds on leading questions"
└── Objection rate: "4 objectionable questions — witness paused on 1 of 4"

WEAKNESS MAP (P1.2 — Performance radar chart):
├── 5 dimensions: Composure, Tactical Discipline, Professionalism, Directness, Consistency
├── Each dimension scored 0–100 (rule-based heuristic analysis + Claude coaching brief)
└── Click dimension → drill into lowest-scoring exchanges for that performance area

TOP 3 COACHING RECOMMENDATIONS:
├── "1. Address the $200 vs $217 dosage discrepancy — prepare a precise explanation."
├── "2. Practice a 3-second pause before answering any leading question."
└── "3. Focus next session on Financial Details (weakest axis: 34/100)."

ACTIONS BAR:
├── [📥 Download PDF]
├── [🔗 Share with Witness] → 7-day expiring token link (witness sees read-only view)
├── [✏️ Annotate Brief] → inline comment mode
└── [📅 Schedule Next Session] → /cases/:caseId/witnesses/:witnessId/session/new

ELEVENLABS COACH NARRATION:
├── Auto-plays on brief load (warm, professional voice)
├── Narrates: session summary, each high-risk moment, top 3 recommendations
└── [⏸ Pause] [⏭ Skip] [🔁 Replay] controls
```

#### ERROR STATES — Coaching Brief

| Error | Display | Recovery |
|-------|---------|----------|
| Brief generation > 3 min | "Taking longer than expected — we'll email you when ready." | Background generation; email deep link on completion |
| PDF export fails | "PDF export failed. [Retry] Brief still available in browser." | Retry; in-browser always available |
| Shared link expired (>7 days) | "This link has expired. Contact your attorney for a new one." | Attorney re-shares from brief viewer |
| Zero flags (clean session) | "No contradictions detected across all indexed prior statements." | Positive framing; recommendations focus on proactive preparation |

---

### FLOW 2.6 — Multi-Session Witness Profile & Progress Tracking (P1.1)

#### HAPPY PATH

```
Witness Profile → /cases/:caseId/witnesses/:witnessId

PROGRESS DASHBOARD:
├── Score trend chart: Session 1 (44) → Session 2 (61) → Session 3 (79)
│   └── Deposition date marked on x-axis as endpoint target
├── Improvement delta: "+35 pts from Session 1" (green callout)
├── Plateau alert: "⚠️ Score unchanged over 3 sessions" (if triggered)
└── System recommendation: "Strong improvement. 1 remaining risk: Documentation dates."

WEAKNESS EVOLUTION:
├── Radar chart: Session 1 vs. Most Recent (side-by-side)
│   └── Green = improved axes; Red = regressed axes
└── Click axis → list of lowest-scoring exchanges for that category

INCONSISTENCY LOG:
├── All confirmed flags across all sessions
├── Status: Resolved / Persisting / New
└── "Persisting" flags auto-injected into Interrogator pre-briefing for next session

SESSION HISTORY:
├── Session 1 | Feb 7 | Score: 44/100 | [View Brief]
├── Session 2 | Feb 14 | Score: 61/100 | [View Brief]
└── Session 3 | Feb 21 | Score: 79/100 | [View Brief]

[CONFIGURE NEXT SESSION] button

System behavior for Session 2+:
├── Interrogator receives: prior weak areas, persisting inconsistency list
├── Interrogator auto-targets weak areas more aggressively
├── Focus Areas: pre-check weak axes (attorney can override)
└── Brief includes automatic delta vs. Session 1
```

---

### FLOW 2.7 — Settings & Admin

```
Attorney Settings → /settings
├── /settings/profile: Name, Email (read-only if SSO), title, practice area
├── /settings/session: Default duration, default aggression level, Objection Copilot default
├── /settings/notifications: Email toggles (brief ready, plateau alert, session reminder)
└── /settings/security: Change password (email/password accounts), active sessions list, [Revoke]

Firm Admin Panel → /admin
├── /admin/users: Active users, pending invites, role changes, deactivation
├── /admin/security: Retention period, SSO config, Behavioral Sentinel firm toggle
├── /admin/analytics: Sessions run, witnesses prepped, average score by attorney
└── /admin/billing: Plan, seats used vs. purchased, renewal date, [Upgrade]
```

---

## 3. NAVIGATION MAP

```
verdict.law/
│
├── / ...................................... B2B Landing (PUBLIC)
│   └── [GET STARTED] → /login or SSO
│
├── /login ................................. Login (PUBLIC)
│   ├── SSO → IdP redirect → /dashboard
│   └── Email/Password → /dashboard
│
├── /onboarding ............................ Firm Setup (PUBLIC + firm token)
│   ├── /onboarding/users .................. Seat Provisioning
│   └── /onboarding/security ............... Security Settings → /admin
│
├── /dashboard ............................. Attorney Dashboard (AUTH)
│   └── [+ NEW CASE] → /cases/new
│
├── /cases ................................. Case List (AUTH)
│   ├── /cases/new ......................... New Case Form
│   └── /cases/:caseId/ .................... Case Detail (AUTH — case owner)
│       ├── (tab: Documents) ............... Upload + Ingestion Status
│       ├── /cases/:caseId/documents/facts . Extracted Fact Review
│       ├── (tab: Witnesses) ............... Witness List
│       ├── (tab: Sessions) ................ Session History
│       ├── (tab: Briefs) .................. Brief History
│       ├── /witnesses/:witnessId ........... Witness Profile + Progress
│       ├── /witnesses/:witnessId/
│       │   session/new .................... Session Configuration → Lobby
│       ├── /session/:id/lobby .............. Pre-Session Lobby
│       ├── /session/:id/live ............... Active Session (Attorney)
│       └── /session/:id/complete ........... Post-Session → Brief Generation
│
├── /briefs/:briefId ....................... Coaching Brief (AUTH or token)
│
├── /witness/session/:sessionId ............ Witness View (TOKEN — no login)
│
├── /settings .............................. User Settings (AUTH)
│   ├── /settings/profile
│   ├── /settings/session
│   ├── /settings/notifications
│   └── /settings/security
│
└── /admin ................................. Firm Admin (AUTH — Admin role)
    ├── /admin/users
    ├── /admin/security
    ├── /admin/analytics
    └── /admin/billing

─────────────────────────────────────────────────────────
CROSS-LINKS (key connections between screens):
─────────────────────────────────────────────────────────
  Brief Viewer ──────────► Schedule Next Session (same witness)
  Brief Viewer ──────────► Case Detail (back)
  Witness Profile ───────► Most recent brief
  Witness Profile ───────► Configure Next Session
  Dashboard ─────────────► Any /cases/:caseId (recent activity)
  Admin Panel ───────────► Case list (read-only admin view)
  Alert Rail (live) ─────► Brief (after session ends)
  Ingestion Complete ────► Fact Review
```

**Authentication Matrix:**

| Route Zone | Requirement |
|-----------|-------------|
| `/`, `/login`, `/onboarding` | Public — no auth |
| `/witness/session/:id` | Witness token in URL — no firm login |
| `/briefs/:briefId` | Attorney JWT OR 7-day share token |
| `/dashboard`, `/cases/*`, `/settings` | Valid JWT + firm membership |
| `/admin/*` | JWT + Admin role claim |

---

## 4. SCREEN INVENTORY

### 4.1 Public / Token-Gated Screens

---

#### B2B Landing Page
- **Route:** `/`
- **Access:** Public
- **Audience:** Law firm decision-makers evaluating VERDICT
- **Key Elements:** ROI headline ("From 16 hrs to 6 hrs per witness"), 4-agent architecture overview, testimonial quote, [REQUEST DEMO] CTA, [LOG IN]
- **Actions:** [REQUEST DEMO] → Calendly/HubSpot | [LOG IN] → `/login`
- **NOT present:** Consumer copy, landlord/tenant content, TikTok UTM flows, SEO guide pages

---

#### Login
- **Route:** `/login`
- **Access:** Public (authenticated users redirect to `/dashboard`)
- **Key Elements:** VERDICT logo, [Sign in with your firm SSO] (primary), email/password fields (non-SSO), [Forgot password?]
- **Actions:** SSO → SAML redirect | Email → POST /api/auth/login → `/dashboard` | Forgot → reset email
- **State Variants:** Default / SSO-only (email fields hidden) / Error ("Invalid credentials") / Locked ("Too many attempts. Contact your firm admin.")

---

#### Witness Session (Token)
- **Route:** `/witness/session/:sessionId`
- **Access:** Witness token (no firm account)
- **Key Elements:** Opposing Counsel avatar, ElevenLabs waveform, "Your Turn" mic indicator, countdown timer, [Need a Moment]
- **NOT shown to witness:** Alert rail, inconsistency flags, objection alerts, live transcript, score
- **State Variants:** Waiting ("Waiting for your session to begin...") / Active / Paused / Complete ("Session complete. Your attorney will be in touch.")

---

#### Coaching Brief — Shared (Witness/Client)
- **Route:** `/briefs/:briefId?token=:token`
- **Access:** 7-day share token OR attorney JWT
- **Witness token view (read-only):** Score, top 3 coaching recommendations, audio clips of flagged moments. NOT shown: raw confidence scores, full alert log, attorney annotations.
- **Attorney JWT view:** Full access — all sections, annotation mode, PDF export, re-share link generator

---

### 4.2 Authenticated Attorney Screens

---

#### Attorney Dashboard
- **Route:** `/dashboard`
- **Access:** Authenticated
- **Key Elements:** Active cases grid (sorted by deposition date, countdown badges), upcoming sessions, recent briefs, platform stats (sessions this month, firm average score trend)
- **Actions:** [+ NEW CASE] → `/cases/new` | Case card → `/cases/:caseId` | Brief card → `/briefs/:briefId`
- **State Variants:** Empty ("Create your first case") / Active (cards sorted soonest deposition first) / Plateau alert banner (if any witness stalled)

---

#### Case Detail
- **Route:** `/cases/:caseId`
- **Access:** Authenticated — case owner + authorized firm members
- **Key Elements:** Case header (name, type, deposition countdown), tab bar (Documents / Witnesses / Sessions / Briefs), context-specific content per tab
- **Actions:** [Upload Document] / [+ Add Witness] / [Configure Session] / [View Brief]
- **State Variants per tab:**
  - Documents: Ingesting / Ready / Failed per document
  - Witnesses: No witnesses (zero-state) / Active witness cards with session counts
  - Sessions: Empty / Session history with score badges
  - Briefs: Empty / Brief cards sorted most recent first

---

#### Extracted Fact Review
- **Route:** `/cases/:caseId/documents/facts`
- **Access:** Authenticated
- **Key Elements:** Parties table, Key Dates table, Disputed Facts list, Prior Sworn Statements (searchable with page/line refs), [Edit] per row, [Add Fact], [Mark as Confirmed] per section
- **Actions:** Edit inline → Save | Add Fact | Confirm section | [CASE IS READY — ADD WITNESS] (unlocks when all confirmed)
- **State Variants:** Unreviewed / Partial (some confirmed) / Ready (all confirmed, CTA active)

---

#### Session Configuration
- **Route:** `/cases/:caseId/witnesses/:witnessId/session/new`
- **Access:** Authenticated
- **Key Elements:** Witness summary, prior session scores (if any), duration picker, Focus Area chips, Aggression Level selector, Objection Copilot toggle, Behavioral Sentinel toggle (if firm-enabled), witness link generator
- **Actions:** [Generate Practice Link] | [Copy Link] | [Resend Email] | [Start Session as Attorney] | [Begin Session] (active when witness connected)
- **State Variants:** First session (clean) / Session 2+ (prior weak areas pre-checked) / Warning (no docs indexed, Detector disabled)

---

#### Session Lobby
- **Route:** `/cases/:caseId/session/:sessionId/lobby`
- **Access:** Authenticated
- **Key Elements:** Session summary card, witness connection status, [Copy Link], [Resend Email], feature toggle confirmation (read-only), [Begin Session Without Witness]
- **Actions:** [BEGIN SESSION] (when witness connected or solo mode)
- **State Variants:** Waiting for witness / Witness connected / Solo mode

---

#### Live Session — Attorney View
- **Route:** `/cases/:caseId/session/:sessionId/live`
- **Access:** Authenticated
- **Key Elements:** Three-panel layout — Left Control / Center Transcript / Right Alert Rail
- **Actions:** Pause / Skip Topic / End Early / Add Note | Per alert: Confirm / Reject / Annotate / Dismiss | Objection Copilot toggle
- **State Variants:** Connecting / Active (all panels live) / Paused / Witness disconnected / Ending

---

#### Witness Profile
- **Route:** `/cases/:caseId/witnesses/:witnessId`
- **Access:** Authenticated
- **Key Elements:** Score trend chart, improvement delta, Weakness Map radar (P1.2), inconsistency log with persisting flags, session history list with scores
- **Actions:** [Configure Next Session] | [View Brief] per session | [Export Progress Report] (PDF, all sessions)
- **State Variants:** Single session (score card only) / Multi-session (trend + radar) / Plateau alert ("⚠️ Score unchanged over 3 sessions")

---

#### Post-Session / Brief Generation
- **Route:** `/cases/:caseId/session/:sessionId/complete`
- **Access:** Authenticated
- **Key Elements:** "Session complete" card, step-by-step generation progress, raw alert count ("3 contradictions, 4 objections captured"), ETA (~2–3 min)
- **Actions:** Review raw alert log while generating | [View Brief] (active once ready)
- **State Variants:** Generating (steps animated) / Ready ([View Brief] CTA active) / Failed ([Retry] with raw log still available)

---

#### Firm Admin Panel
- **Route:** `/admin`
- **Access:** JWT + Admin role
- **Key Elements:** Seat management, security settings, SSO configuration, usage analytics, billing summary
- **Actions:** Invite users / Change roles / Revoke access / Update retention period / Upgrade plan

---

## 5. DECISION POINTS

### 5.1 Authentication & Authorization

```
IF route requires auth AND valid JWT AND not expired
THEN render with user context

ELSE IF JWT expired AND refresh token valid
THEN silently refresh JWT → proceed
ELSE redirect to /login?redirect=[current_path]

IF route is /witness/session/:id
  IF valid witness token in URL
  THEN render witness view (no firm auth required)
  ELSE IF expired token
  THEN "This practice link has expired. Contact your attorney."
  ELSE IF used token (session completed)
  THEN "This session has already been completed."

IF route is /admin/*
  IF user.role == "admin" THEN render admin panel
  ELSE redirect /dashboard ("Admin access required")

IF route is /cases/:caseId AND user not in case.authorized_users
THEN 403 → "You don't have access to this case."
```

---

### 5.2 Document Ingestion Readiness Gate

```
IF attorney configures session AND case.documents.ingested_count == 0
THEN
  Show WARNING: "No documents indexed — Inconsistency Detector disabled for this session"
  Allow session (Interrogator + Objection Copilot still active)
  Inconsistency Detector greyed out in feature toggles

ELSE IF case.documents.ingestion_status == "in_progress"
THEN
  [Configure Session] disabled
  Tooltip: "Waiting for document indexing to complete (ETA: Xm Ys)"

ELSE IF case.documents.ingested_count >= 1
THEN
  All features available
  Inconsistency Detector pre-briefed with indexed statements
```

---

### 5.3 Inconsistency Detector — Confidence Routing

```
run InconsistencyDetector(answer, nia_index)
→ { contradiction_confidence: float, prior_quote: str, page: int, line: int }

IF confidence >= 0.75
  IF BehavioralSentinel.active AND emotion IN [Fear, Contempt] AND duration >= 0.8s
    flag.risk = "HIGH IMPEACHMENT RISK"
    flag.confidence += 0.05 (behavioral corroboration weight)
  ELSE
    flag.risk = "CONTRADICTION"
  → fire live alert in rail (≤ 4s)
  → log to session record

ELSE IF confidence 0.50–0.74
  → add to secondary_review_queue
  → surface in brief under "Possible Inconsistencies — Attorney Review"
  → do NOT fire live rail alert

ELSE confidence < 0.50
  → discard silently
```

---

### 5.4 Nemotron API Unavailability (Graceful Degradation)

```
IF Nemotron response > 5s OR returns error
THEN
  Inconsistency Detector:
    Fall back to Claude-only semantic comparison
    Raise confidence threshold 0.75 → 0.85 (reduces false positives)
    Show rail badge: "⚠️ Scoring: Claude-only (Nemotron unavailable)"
    Session continues uninterrupted

  Argument Strength Scoring (P1.3):
    Disabled for session
    Note in brief: "Argument scores unavailable — API degradation this session"
```

---

### 5.5 ElevenLabs API Unavailability (Graceful Degradation)

```
IF ElevenLabs TTS fails:
  Questions render as text cards in center transcript
  Banner: "Audio paused — questions displayed as text"
  Witness view: large centered text replaces voice

IF ElevenLabs STT fails:
  Fall back to browser Web Speech API (lower accuracy)
  Banner: "Voice recognition in fallback mode"
  Attorney can correct transcript post-session before brief generation

IF both TTS and STT fail:
  Full text-only mode
  Banner: "Text-only mode active — voice services temporarily unavailable"
  Attorney types/selects questions; witness types answers
```

---

### 5.6 Behavioral Sentinel — Activation Gate

```
IF firm.behavioral_sentinel_enabled == false
  Feature hidden in all UI — no camera permission ever requested

ELSE IF firm.behavioral_sentinel_enabled == true AND session.sentinel_opted_in == false
  Toggle visible in session config — OFF by default
  Attorney must explicitly enable per session

ELSE IF session.sentinel_opted_in == true
  Witness consent screen shown before session:
    "VERDICT may analyze facial expressions to provide composure coaching.
     No video is recorded or transmitted. Analysis runs on your device only."

  IF witness grants camera permission
    MediaPipe Face Mesh initializes client-side (430 landmarks, ≥15fps)
    Behavioral Sentinel active — third alert lane appears in attorney rail

  IF witness denies permission
    Silent degradation — session continues without facial analysis
    Attorney notified: "Behavioral Sentinel inactive — camera access not granted"
    No indication shown to witness that the feature was attempted
```

---

### 5.7 Session 2+ Adaptive Behavior

```
IF witness.session_count >= 2
  Interrogator pre-briefing includes:
    prior_session_weak_areas (axes scored < 60)
    persisting_inconsistencies (flags confirmed across multiple sessions)
    prior_question_log (prevents exact repetition)

  Session configuration:
    Focus areas: pre-check prior weak axes (attorney can override)
    Aggression: recommend +1 level if prior score < 65

  Coaching brief:
    Adds "Progress vs. Session 1" delta section automatically
    Score delta prominent: "Session 3: 79/100 (+35 from Session 1)"

IF witness.score_trend shows no improvement after 3 sessions
  Dashboard: "⚠️ Witness plateau detected for [Name] — review coaching strategy"
  Witness Profile: plateau banner + coaching note
  Brief: "Plateau Alert — Consider revising prep approach or evaluating settlement implications"
```

---

## 6. ERROR HANDLING

### 6.1 HTTP 404 — Not Found

- **Display:** "Case not found" card (under `/cases/*`) or generic "Page not found" (global). [Return to Dashboard]. No route suggestions — enterprise tool.
- **System:** Log to analytics; repeated 404 on same path → ops alert.

---

### 6.2 HTTP 500 — Server Error

- **Transient:** Toast "Something went wrong. [Retry]" (3s auto-dismiss + retry button stays)
- **Page-level:** "VERDICT is experiencing an issue. Our team has been notified." + `status.verdict.law` link
- **System:** Sentry + Databricks error event; PagerDuty if error rate > 2% over 5 minutes
- **Session protection:** All session events persisted every 60 seconds — maximum 60 seconds of data loss on any failure

---

### 6.3 Network Offline

- **Display:** Persistent top banner: "📡 Connection lost — session data is being saved locally"
- **During active session:** Interrogator pauses; transcript buffered in IndexedDB; alert rail shows "Offline — alerts resume on reconnect"; timer continues (deposition clock doesn't pause)
- **On reconnect:** Banner dismisses; buffered events flushed to server; session resumes automatically

---

### 6.4 HTTP 403 — Access Denied

- **Display:** "You don't have permission to access this case." No case details revealed. [Return to Dashboard].
- **System:** Log unauthorized attempt; repeated from same user → ops alert + potential account review

---

### 6.5 Form Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| Case Name | Required, 3–120 chars | "Case name must be between 3 and 120 characters" |
| Case Type | Required | "Please select a case type" |
| Deposition Date | Must be in future | "Deposition date must be in the future" |
| Witness Name | Required, 2–80 chars | "Please enter the witness's full name" |
| Witness Email | Valid RFC 5322 | "Please enter a valid email address" |
| Session Duration | Required selection | "Please select a session duration" |
| Document upload | PDF/DOCX/TXT, ≤200MB | "File must be PDF, DOCX, or TXT and under 200MB" |

**Validation behavior:** Fires on `blur` per field. Submit blocked until all errors clear. No page-level validation on submit.

---

### 6.6 Session Timeout / JWT Expiry

- **In active session (5 min warning):** Non-dismissable modal: "Your session will expire in 5 minutes. [Extend]" → silently re-auths via SSO or prompts password re-entry
- **Browsing dashboard:** Modal: "Your session has expired. Log in to continue." Email pre-filled.
- **Session data:** All events already persisted to Databricks — zero data loss from JWT expiry

---

### 6.7 Ingestion Pipeline Failure

- **Per-document:** 🔴 "Ingestion failed. [Retry] [View Error Details]"
- **Error detail modal:** Specific reason (e.g., "Could not extract text from page 47 — may be image-based")
- **System:** Exponential backoff retry queue (3 attempts max); ops alert if all retries exhausted

---

## 7. RESPONSIVE BEHAVIOR

### 7.1 Mobile (< 768px)

**Important:** VERDICT v1.0 is web browser only. Native mobile apps are v2.0. Mobile browser support is provided primarily for the **witness view** — the attorney live session experience is strongly recommended on desktop only.

**Witness view on mobile (primary mobile use case):**
- Full-screen Opposing Counsel avatar + waveform
- "Your Turn" mic indicator large and centered
- [Need a Moment] button full-width
- Timer displayed at top
- Tested on: iOS Safari, Android Chrome

**Attorney views on mobile (degraded — read-only tasks only):**
- Dashboard: Single-column case cards, swipe for deposition countdown
- Case Detail: Tab strip horizontal-scrollable; document upload available
- Brief Viewer: Stacked single-column; radar chart full-width below score card
- Live Session on mobile: NOT recommended — alert rail collapses to notification badge; [Show Alerts] FAB opens bottom sheet

---

### 7.2 Tablet (768px–1024px)

- Session configuration: Single-column form, no persistent sidebar
- Live session: Alert rail collapses to 240px right panel; collapse toggle available
- Brief: Single-column; radar chart full-width; audio player pinned below score card
- Case Detail: Tabs retained; document upload and witness management usable

---

### 7.3 Desktop (≥1024px) — Primary Experience

- **Live session:** Three-panel layout — 220px control / flexible transcript / 320px alert rail
- **Brief Viewer:** Two-column — score/summary left, inconsistency detail right; radar full-width below
- **Witness Profile:** Side-by-side radar comparison (Session 1 vs. Latest)
- **Keyboard shortcuts:** `Space` = pause/resume | `Cmd+N` = add note | `Esc` = close modals | `Cmd+E` = end session (with confirmation)
- **Minimum recommended resolution:** 1280 × 768

---

## 8. ANIMATIONS & TRANSITIONS

### 8.1 Page Transitions

| Transition | Duration | Easing | Notes |
|-----------|----------|--------|-------|
| Dashboard → Case Detail | 250ms | `ease-out` | Slide right; case header expands from card |
| Case Detail → Live Session | 400ms | `ease-in-out` | Full-screen takeover — session UI expands from center |
| Live Session → Post-Session | 300ms | `ease-in` | Transcript fades; brief generation card fades in |
| Post-Session → Brief | 350ms | `ease-out` | Brief sections cascade in top to bottom |
| Any modal open | 200ms | `ease-out` | Scale 95%→100% + opacity 0→1 |
| Any modal close | 150ms | `ease-in` | Scale 100%→95% + opacity 1→0 |

---

### 8.2 Alert Rail — Micro-Interactions

```
New Objection Alert fires:
  1. Rail badge: increments with pop (scale 1→1.3→1, 150ms)
  2. Alert card: slides down from top of rail (300ms, spring)
  3. Card background: red-50 → white fade (1.5s — draws eye, then settles)
  4. Optional audio: soft chime ≤500ms (attorney-configurable)

New Inconsistency Alert fires:
  1. Same badge increment
  2. Card background: red pulse (200ms) — more urgent than objection
  3. HIGH IMPEACHMENT RISK: card border pulses red × 2 cycles then settles

Alert confirmed:
  1. [✓ Confirm] clicked → green flash (200ms) → card fades to grey "Confirmed" state
  2. "✓ Confirmed" chip added to card

Alert rejected:
  1. Card slides out right (200ms) → removed from rail
```

---

### 8.3 Session State Animations

```
Session Start:
  - Timer begins counting down
  - Alert rail: "Monitoring initializing..." spinner → "Monitoring active" (green pulse)
  - Transcript: "Session beginning..." placeholder → first question fades in
  - ElevenLabs waveform: activates below Opposing Counsel avatar

Interrogator speaking:
  - Avatar: subtle green glow pulse synced to audio amplitude
  - Waveform: 20-bar frequency visualization, indigo (#6366F1)

Witness responding (attorney view):
  - "Witness" label activates in transcript header
  - Attorney-side waveform: green bars showing witness audio level

Session Pause:
  - Timer color: blue → amber
  - Transcript: semi-transparent overlay "Session paused"
  - Alert rail: grey overlay "Monitoring paused"

Session End:
  - All panels fade
  - "Session complete" card expands from center
  - Brief generation steps animate sequentially
```

---

### 8.4 Coaching Brief Animations

```
Brief generation progress (on post-session screen):
  Step 1: "Analyzing exchanges..." → ✅ checkmark (~2s)
  Step 2: "Scoring inconsistencies..." → ✅ (~4s)
  Step 3: "Building Weakness Map..." → ✅ (~6s)
  Step 4: "Brief ready" → full brief card reveals (cascade top-to-bottom, 500ms)

Score card reveal:
  - Number: counts up from 0 → final (1.2s, ease-out)
  - Color: transitions through green→amber→red to resolve at actual value
  - Radar chart: axes animate outward from center (600ms, staggered per axis, 80ms delay each)

Inconsistency card expand:
  - Click: height animates collapsed (40px) → full (ease-out, 250ms)
  - Audio clip player: waveform renders inline on expand
```

---

### 8.5 Loading States

| Component | Loading Behavior |
|-----------|-----------------|
| Dashboard case cards | Skeleton shimmer, 1.5s cycle |
| Document ingestion | Animated progress bar + live page count ticker per document |
| Fact review page | Skeleton table rows (3 full-width + 2 partial) |
| Brief generation | Step-by-step indicator with estimated time |
| Radar chart (Weakness Map) | Skeleton axes → populated (600ms transition) |
| Alert rail (session start) | "Monitoring initializing..." spinner → "Monitoring active" |
| Witness profile scores | Skeleton trend chart → populated with animation |

---

*APP_FLOW.md — VERDICT v1.0.0 — Hackathon Edition*  
*B2B Deposition Coaching Platform — Built for Litigation Attorneys at Midsize Law Firms*  
*Team VoiceFlow Intelligence | NYU Startup Week Buildathon 2026 | AI Automation — August.law Sponsor Track*
