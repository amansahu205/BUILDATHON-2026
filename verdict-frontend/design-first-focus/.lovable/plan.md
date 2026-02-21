

# VERDICT — Frontend Implementation Plan (Updated)
> AI-Powered Deposition Coaching & Trial Preparation Platform  
> Every screen • API-only data layer • React + Vite + Tailwind + shadcn/ui

---

## Phase 1: Foundation & Design System

### 1.1 Design System & Theme
- Dark professional color palette suited for enterprise legal SaaS (navy/slate tones, amber/red for alerts)
- Typography hierarchy for legal content (transcript readability, data tables)
- Custom CSS variables for VERDICT brand colors

### 1.2 Layout Components
- **App Shell** with authenticated sidebar navigation (Cases, Dashboard, Settings, Admin)
- **Case Layout** with persistent case header (name, type, deposition countdown badge) and tab navigation
- **Public Layout** for landing, login, onboarding pages (no sidebar)

### 1.3 API Service Layer
- Typed API service modules for each domain: `auth`, `cases`, `documents`, `witnesses`, `sessions`, `briefs`, `admin`
- Axios instance with JWT interceptor, refresh token handling, and base URL configuration
- React Query hooks wrapping each API call for caching and loading states

### 1.4 Route Structure & Auth Guards
- Protected route wrapper checking JWT validity
- Admin role guard for `/admin/*` routes
- Token-based access for witness session and shared briefs
- Redirect-to-login with return URL preservation

---

## Phase 2: Public & Auth Screens

### 2.1 B2B Landing Page (`/`)
- Hero section with ROI headline ("From 16 hrs to 6 hrs per witness")
- 4-agent architecture visual overview
- Testimonial section
- [REQUEST DEMO] and [LOG IN] CTAs

### 2.2 Login Page (`/login`)
- VERDICT logo and branding
- SSO button (Sign in with your firm SSO) — primary
- Email/password form — secondary
- Forgot password link
- Error and lockout state variants

### 2.3 Firm Onboarding Flow (`/onboarding`)
- 3-step progress bar wizard:
  - Step 1: Firm Configuration (name, admin, SSO toggle or password policy)
  - Step 2: Seat Provisioning (CSV upload or manual add, role dropdown)
  - Step 3: Security Settings (retention, case isolation, Behavioral Sentinel toggle)
- Token validation on entry, error states for expired/invalid tokens

---

## Phase 3: Core Attorney Screens

### 3.1 Attorney Dashboard (`/dashboard`)
- Active cases grid sorted by deposition date with countdown badges
- Upcoming sessions list
- Recent briefs cards
- Platform stats (sessions this month, firm average score trend)
- Empty state: "Create your first case"
- [+ NEW CASE] CTA

### 3.2 Case List (`/cases`)
- Filterable, sortable case list with search
- Case cards showing name, type, witness count, deposition countdown
- [+ NEW CASE] button

### 3.3 New Case Form (`/cases/new`)
- Case Name, Case Type dropdown (Medical Malpractice, Employment Discrimination, etc.)
- Opposing Firm (optional), Deposition Date picker
- Validation rules (name 3–120 chars, type required)

### 3.4 Case Detail (`/cases/:caseId`)
- Persistent case header with deposition countdown
- Tab navigation: Documents / Witnesses / Sessions / Briefs
- **Documents Tab**: Drag-and-drop upload zone, per-file progress bars, ingestion status cards (Uploading/Indexing/Ready/Failed), document type tags
- **Witnesses Tab**: Witness cards with session counts, [+ ADD WITNESS] modal
- **Sessions Tab**: Session history with score badges
- **Briefs Tab**: Brief cards sorted most recent first

### 3.5 Fact Review (`/cases/:caseId/documents/facts`)
- Parties table with inline edit
- Key Dates table with date, event, source doc + page reference
- Disputed Facts highlighted list
- Prior Sworn Statements searchable index
- [Add Fact], [Mark as Confirmed] per section
- [CASE IS READY — ADD WITNESS] CTA (active when all confirmed)

---

## Phase 4: Witness & Session Setup

### 4.1 Witness Profile (`/cases/:caseId/witnesses/:witnessId`)
- Score trend chart (line chart across sessions)
- Improvement delta callout
- Weakness Map radar chart (6 axes + composure if Sentinel active)
- Inconsistency log (Resolved / Persisting / New status)
- Session history with [View Brief] links
- Plateau alert banner when triggered
- [Configure Next Session] button

### 4.2 Session Configuration (`/cases/:caseId/witnesses/:witnessId/session/new`)
- Witness summary card with prior session scores
- Duration picker (15/30/45/60 min)
- Focus Area multi-select chips (Timeline, Financial, Communications, Relationships, Actions, Prior Statements)
- Interrogator Aggression level selector (Standard/Elevated/High-Stakes)
- Objection Copilot toggle
- Behavioral Sentinel toggle (shown only if firm-enabled)
- [Generate Practice Link] and [Start Session as Attorney] buttons

### 4.3 Session Lobby (`/cases/:caseId/session/:sessionId/lobby`)
- Session summary card (witness, case, duration, focus areas, docs indexed, prior sessions)
- Witness connection status indicator
- [Copy Link] and [Resend Email] buttons
- Feature toggle confirmation (read-only)
- [BEGIN SESSION] / [BEGIN SESSION WITHOUT WITNESS]

---

## Phase 5: Live Session (Three-Panel Layout)

### 5.1 Attorney Live Session View (`/cases/:caseId/session/:sessionId/live`)
- **Left Panel (220px)**: Session timer (color-coded: amber < 10min, red < 5min), current topic, question counter, [Pause], [Skip Topic], [End Early]
- **Center Panel (flexible)**: Speaker-tagged auto-scrolling transcript, flagged exchanges with red border, [Export Transcript]
- **Right Panel (320px)**: Live Alert Rail — Objection Copilot alerts (🔴 with FRE rule), Inconsistency Detector alerts (confidence score, prior quote, page/line), Behavioral Sentinel alerts (🟠 experimental label, AU codes), per-alert actions [Confirm/Reject/Annotate/Dismiss]
- **Bottom Bar**: [Add Note] for timestamped annotations
- State variants: Connecting, Active, Paused, Witness Disconnected, Ending
- WebSocket connection status indicator and degradation banners

### 5.2 Witness Session View (`/witness/session/:sessionId`)
- Token-gated, minimal single-panel design
- Opposing Counsel avatar (centered)
- Audio waveform visualizer placeholder
- "Your Turn" mic indicator
- Session countdown timer
- [Need a Moment] pause button
- States: Waiting / Active / Paused / Complete
- No alert rail, no transcript, no scores visible

### 5.3 Post-Session / Brief Generation (`/cases/:caseId/session/:sessionId/complete`)
- "Session complete" card
- Step-by-step generation progress animation
- Raw alert count summary
- ETA display
- [View Brief] CTA (active once ready)

---

## Phase 6: Coaching Brief

### 6.1 Coaching Brief Viewer (`/briefs/:briefId`)
- **Score Summary Card**: Session score (0–100, color-coded), delta vs Session 1, consistency rate, alert totals
- **Inconsistencies Section**: Expanded confirmed flags with timestamp, audio play button, highlighted phrases, prior statement quote with page/line, confidence score, impeachment risk badge, coach note. Collapsed secondary queue (0.50–0.74 confidence)
- **Objections Section**: Events with timestamp, question text, FRE rule, training notes, objection rate
- **Weakness Map**: 6-axis radar chart (+ composure if Sentinel was active), click-to-drill
- **Top 3 Coaching Recommendations**: Actionable text items
- **Actions Bar**: [Download PDF], [Share with Witness], [Annotate Brief], [Schedule Next Session]
- **Coach Narration Player**: Play/Pause/Skip/Replay controls
- Witness token view: read-only subset (no raw confidence, no annotations, no full alert log)

---

## Phase 7: Settings & Admin

### 7.1 Attorney Settings (`/settings`)
- Profile tab: Name, email (read-only if SSO), title, practice area
- Session Defaults tab: Default duration, aggression level, Objection Copilot default
- Notifications tab: Email toggles (brief ready, plateau alert, session reminder)
- Security tab: Change password, active sessions list with [Revoke]

### 7.2 Firm Admin Panel (`/admin`) — Static Mockup
- **Users tab**: Static display of active users, pending invites, role badges — no real CRUD
- **Security tab**: Static read-only view of retention period, SSO config status, Behavioral Sentinel firm toggle
- **Analytics tab**: Static charts showing sessions run, witnesses prepped, average score by attorney — hardcoded display data
- **~~Billing~~**: Removed — no billing, plan management, or Stripe integration
- All admin content is presentational only (no API calls, no mutations) to demonstrate enterprise readiness for judges

---

## Phase 8: Error States & Edge Cases

- Comprehensive error handling across all screens per the APP_FLOW specs
- 404/403 pages with contextual messaging
- Offline/disconnection handling for WebSocket-dependent screens
- Graceful degradation banners (ElevenLabs down, Nemotron unavailable, Nia offline)
- Loading skeletons and empty states for every data-driven component

