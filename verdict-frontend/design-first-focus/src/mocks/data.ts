// ============================================================
// VERDICT — Hardcoded mock data for all features
// ============================================================

import type {
  User, Case, CaseDocument, Witness, Session, SessionLobby,
  Brief, BriefInconsistency, BriefObjection, FactReview,
  AttorneySettings, ActiveSession, LiveSessionState,
  AuthTokens, LoginResponse,
} from "@/types";

// ---- Mock User (Attorney) ----
export const MOCK_USER: User = {
  id: "usr_001",
  email: "sarah.chen@morrison-associates.com",
  name: "Sarah Chen",
  role: "admin",
  firmId: "firm_001",
  title: "Senior Litigation Partner",
  practiceArea: "Medical Malpractice",
  ssoEnabled: false,
  createdAt: "2024-06-15T10:00:00Z",
};

export const MOCK_TOKENS: AuthTokens = {
  accessToken: "mock-access-token-xyz",
  refreshToken: "mock-refresh-token-xyz",
};

export const MOCK_LOGIN_RESPONSE: LoginResponse = {
  user: MOCK_USER,
  tokens: MOCK_TOKENS,
};

// ---- Cases ----
const depositionDate1 = new Date();
depositionDate1.setDate(depositionDate1.getDate() + 12);

const depositionDate2 = new Date();
depositionDate2.setDate(depositionDate2.getDate() + 5);

const depositionDate3 = new Date();
depositionDate3.setDate(depositionDate3.getDate() + 28);

export const MOCK_CASES: Case[] = [
  {
    id: "case_001",
    name: "Martinez v. St. Luke's Medical Center",
    caseType: "medical_malpractice",
    opposingFirm: "Hartwell & Associates",
    depositionDate: depositionDate1.toISOString(),
    witnessCount: 3,
    documentCount: 24,
    sessionCount: 7,
    status: "active",
    createdAt: "2024-09-10T08:00:00Z",
    updatedAt: "2025-02-18T14:30:00Z",
  },
  {
    id: "case_002",
    name: "Thompson v. Axiom Industries",
    caseType: "employment_discrimination",
    opposingFirm: "Baker Donnelley LLP",
    depositionDate: depositionDate2.toISOString(),
    witnessCount: 2,
    documentCount: 18,
    sessionCount: 4,
    status: "active",
    createdAt: "2024-11-20T09:00:00Z",
    updatedAt: "2025-02-15T11:00:00Z",
  },
  {
    id: "case_003",
    name: "Greenfield HOA v. Apex Construction",
    caseType: "commercial_litigation",
    depositionDate: depositionDate3.toISOString(),
    witnessCount: 1,
    documentCount: 9,
    sessionCount: 1,
    status: "active",
    createdAt: "2025-01-05T10:00:00Z",
    updatedAt: "2025-02-10T09:00:00Z",
  },
];

// ---- Documents ----
export const MOCK_DOCUMENTS: Record<string, CaseDocument[]> = {
  case_001: [
    { id: "doc_001", caseId: "case_001", fileName: "Martinez_MedicalRecords_2023.pdf", fileSize: 4_200_000, mimeType: "application/pdf", status: "ready", documentType: "medical_record", pageCount: 142, uploadedAt: "2024-09-12T10:00:00Z", indexedAt: "2024-09-12T10:15:00Z" },
    { id: "doc_002", caseId: "case_001", fileName: "DrPatel_PriorDeposition.pdf", fileSize: 2_800_000, mimeType: "application/pdf", status: "ready", documentType: "deposition", pageCount: 87, uploadedAt: "2024-09-12T10:05:00Z", indexedAt: "2024-09-12T10:22:00Z" },
    { id: "doc_003", caseId: "case_001", fileName: "StLukes_IncidentReport.pdf", fileSize: 890_000, mimeType: "application/pdf", status: "ready", documentType: "exhibit", pageCount: 12, uploadedAt: "2024-09-13T08:00:00Z", indexedAt: "2024-09-13T08:05:00Z" },
    { id: "doc_004", caseId: "case_001", fileName: "ExpertReport_DrNguyen.pdf", fileSize: 3_100_000, mimeType: "application/pdf", status: "indexing", documentType: "expert_report", pageCount: 45, uploadedAt: "2025-02-18T14:00:00Z" },
    { id: "doc_005", caseId: "case_001", fileName: "Correspondence_Hospital_2024.pdf", fileSize: 1_500_000, mimeType: "application/pdf", status: "ready", documentType: "correspondence", pageCount: 33, uploadedAt: "2024-10-01T09:00:00Z", indexedAt: "2024-10-01T09:10:00Z" },
  ],
  case_002: [
    { id: "doc_010", caseId: "case_002", fileName: "Thompson_HR_File.pdf", fileSize: 1_800_000, mimeType: "application/pdf", status: "ready", documentType: "exhibit", pageCount: 56, uploadedAt: "2024-11-22T10:00:00Z", indexedAt: "2024-11-22T10:12:00Z" },
    { id: "doc_011", caseId: "case_002", fileName: "Performance_Reviews_2021-2024.pdf", fileSize: 2_200_000, mimeType: "application/pdf", status: "ready", documentType: "exhibit", pageCount: 78, uploadedAt: "2024-11-22T10:05:00Z", indexedAt: "2024-11-22T10:20:00Z" },
    { id: "doc_012", caseId: "case_002", fileName: "Email_Thread_Termination.pdf", fileSize: 450_000, mimeType: "application/pdf", status: "ready", documentType: "correspondence", pageCount: 15, uploadedAt: "2024-12-01T08:00:00Z", indexedAt: "2024-12-01T08:05:00Z" },
  ],
  case_003: [
    { id: "doc_020", caseId: "case_003", fileName: "Construction_Contract.pdf", fileSize: 5_600_000, mimeType: "application/pdf", status: "ready", documentType: "exhibit", pageCount: 210, uploadedAt: "2025-01-06T09:00:00Z", indexedAt: "2025-01-06T09:25:00Z" },
  ],
};

// ---- Witnesses ----
export const MOCK_WITNESSES: Record<string, Witness[]> = {
  case_001: [
    { id: "wit_001", caseId: "case_001", name: "Dr. Rajesh Patel", role: "Treating Physician", sessionCount: 4, latestScore: 72, scoreTrend: [45, 58, 66, 72], plateauAlert: false, createdAt: "2024-09-15T10:00:00Z" },
    { id: "wit_002", caseId: "case_001", name: "Nurse Linda Okafor", role: "Attending Nurse", sessionCount: 2, latestScore: 61, scoreTrend: [52, 61], plateauAlert: false, createdAt: "2024-10-01T10:00:00Z" },
    { id: "wit_003", caseId: "case_001", name: "Carlos Martinez", role: "Plaintiff", sessionCount: 1, latestScore: 38, scoreTrend: [38], plateauAlert: false, createdAt: "2024-11-10T10:00:00Z" },
  ],
  case_002: [
    { id: "wit_010", caseId: "case_002", name: "David Thompson", role: "Plaintiff (Former Employee)", sessionCount: 3, latestScore: 68, scoreTrend: [41, 55, 68], plateauAlert: false, createdAt: "2024-12-01T10:00:00Z" },
    { id: "wit_011", caseId: "case_002", name: "Karen Miller", role: "HR Director", sessionCount: 1, latestScore: 54, scoreTrend: [54], plateauAlert: true, createdAt: "2025-01-10T10:00:00Z" },
  ],
  case_003: [
    { id: "wit_020", caseId: "case_003", name: "Frank Greenfield", role: "HOA Board President", sessionCount: 1, latestScore: 47, scoreTrend: [47], plateauAlert: false, createdAt: "2025-01-15T10:00:00Z" },
  ],
};

// ---- Sessions ----
export const MOCK_SESSIONS: Record<string, Session[]> = {
  case_001: [
    { id: "ses_001", caseId: "case_001", witnessId: "wit_001", witnessName: "Dr. Rajesh Patel", config: { witnessId: "wit_001", durationMinutes: 30, focusAreas: ["timeline", "actions"], aggressionLevel: "standard", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 45, briefId: "brief_001", startedAt: "2024-10-05T14:00:00Z", endedAt: "2024-10-05T14:32:00Z", createdAt: "2024-10-05T13:50:00Z" },
    { id: "ses_002", caseId: "case_001", witnessId: "wit_001", witnessName: "Dr. Rajesh Patel", config: { witnessId: "wit_001", durationMinutes: 30, focusAreas: ["timeline", "financial", "communications"], aggressionLevel: "elevated", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 58, briefId: "brief_002", startedAt: "2024-10-20T14:00:00Z", endedAt: "2024-10-20T14:35:00Z", createdAt: "2024-10-20T13:50:00Z" },
    { id: "ses_003", caseId: "case_001", witnessId: "wit_001", witnessName: "Dr. Rajesh Patel", config: { witnessId: "wit_001", durationMinutes: 45, focusAreas: ["timeline", "actions", "prior_statements"], aggressionLevel: "elevated", objectionCopilot: true, behavioralSentinel: true }, status: "complete", score: 66, briefId: "brief_003", startedAt: "2024-11-15T14:00:00Z", endedAt: "2024-11-15T14:48:00Z", createdAt: "2024-11-15T13:50:00Z" },
    { id: "ses_004", caseId: "case_001", witnessId: "wit_001", witnessName: "Dr. Rajesh Patel", config: { witnessId: "wit_001", durationMinutes: 45, focusAreas: ["timeline", "actions", "prior_statements", "financial"], aggressionLevel: "high_stakes", objectionCopilot: true, behavioralSentinel: true }, status: "complete", score: 72, briefId: "brief_004", startedAt: "2025-01-10T14:00:00Z", endedAt: "2025-01-10T14:47:00Z", createdAt: "2025-01-10T13:50:00Z" },
    { id: "ses_005", caseId: "case_001", witnessId: "wit_002", witnessName: "Nurse Linda Okafor", config: { witnessId: "wit_002", durationMinutes: 30, focusAreas: ["timeline", "actions"], aggressionLevel: "standard", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 52, briefId: "brief_005", startedAt: "2024-11-01T10:00:00Z", endedAt: "2024-11-01T10:33:00Z", createdAt: "2024-11-01T09:50:00Z" },
    { id: "ses_006", caseId: "case_001", witnessId: "wit_002", witnessName: "Nurse Linda Okafor", config: { witnessId: "wit_002", durationMinutes: 30, focusAreas: ["timeline", "actions", "communications"], aggressionLevel: "elevated", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 61, briefId: "brief_006", startedAt: "2025-01-20T10:00:00Z", endedAt: "2025-01-20T10:34:00Z", createdAt: "2025-01-20T09:50:00Z" },
    { id: "ses_007", caseId: "case_001", witnessId: "wit_003", witnessName: "Carlos Martinez", config: { witnessId: "wit_003", durationMinutes: 30, focusAreas: ["timeline", "relationships"], aggressionLevel: "standard", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 38, briefId: "brief_007", startedAt: "2025-02-01T10:00:00Z", endedAt: "2025-02-01T10:31:00Z", createdAt: "2025-02-01T09:50:00Z" },
  ],
  case_002: [
    { id: "ses_010", caseId: "case_002", witnessId: "wit_010", witnessName: "David Thompson", config: { witnessId: "wit_010", durationMinutes: 30, focusAreas: ["timeline", "communications"], aggressionLevel: "standard", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 41, briefId: "brief_010", startedAt: "2024-12-10T14:00:00Z", endedAt: "2024-12-10T14:33:00Z", createdAt: "2024-12-10T13:50:00Z" },
    { id: "ses_011", caseId: "case_002", witnessId: "wit_010", witnessName: "David Thompson", config: { witnessId: "wit_010", durationMinutes: 45, focusAreas: ["timeline", "communications", "relationships"], aggressionLevel: "elevated", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 55, briefId: "brief_011", startedAt: "2025-01-05T14:00:00Z", endedAt: "2025-01-05T14:48:00Z", createdAt: "2025-01-05T13:50:00Z" },
    { id: "ses_012", caseId: "case_002", witnessId: "wit_010", witnessName: "David Thompson", config: { witnessId: "wit_010", durationMinutes: 45, focusAreas: ["timeline", "communications", "relationships", "prior_statements"], aggressionLevel: "high_stakes", objectionCopilot: true, behavioralSentinel: true }, status: "complete", score: 68, briefId: "brief_012", startedAt: "2025-02-05T14:00:00Z", endedAt: "2025-02-05T14:46:00Z", createdAt: "2025-02-05T13:50:00Z" },
    { id: "ses_013", caseId: "case_002", witnessId: "wit_011", witnessName: "Karen Miller", config: { witnessId: "wit_011", durationMinutes: 30, focusAreas: ["actions", "communications"], aggressionLevel: "standard", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 54, briefId: "brief_013", startedAt: "2025-02-10T10:00:00Z", endedAt: "2025-02-10T10:32:00Z", createdAt: "2025-02-10T09:50:00Z" },
  ],
  case_003: [
    { id: "ses_020", caseId: "case_003", witnessId: "wit_020", witnessName: "Frank Greenfield", config: { witnessId: "wit_020", durationMinutes: 30, focusAreas: ["timeline", "financial"], aggressionLevel: "standard", objectionCopilot: true, behavioralSentinel: false }, status: "complete", score: 47, briefId: "brief_020", startedAt: "2025-01-25T14:00:00Z", endedAt: "2025-01-25T14:33:00Z", createdAt: "2025-01-25T13:50:00Z" },
  ],
};

// ---- Fact Review ----
export const MOCK_FACT_REVIEWS: Record<string, FactReview> = {
  case_001: {
    parties: [
      { id: "p1", name: "Carlos Martinez", role: "Plaintiff", description: "Patient who underwent spinal surgery", confirmed: true },
      { id: "p2", name: "St. Luke's Medical Center", role: "Defendant", description: "Hospital where surgery was performed", confirmed: true },
      { id: "p3", name: "Dr. Rajesh Patel", role: "Defendant (Surgeon)", description: "Attending orthopedic surgeon", confirmed: true },
      { id: "p4", name: "Nurse Linda Okafor", role: "Witness", description: "Attending nurse during procedure", confirmed: false },
    ],
    keyDates: [
      { id: "kd1", date: "2023-03-15", event: "Initial consultation with Dr. Patel", sourceDocId: "doc_001", sourceDocName: "Martinez Medical Records", pageReference: "12", confirmed: true },
      { id: "kd2", date: "2023-04-22", event: "Pre-operative imaging (MRI)", sourceDocId: "doc_001", sourceDocName: "Martinez Medical Records", pageReference: "34", confirmed: true },
      { id: "kd3", date: "2023-05-10", event: "Spinal fusion surgery performed", sourceDocId: "doc_003", sourceDocName: "Incident Report", pageReference: "1", confirmed: true },
      { id: "kd4", date: "2023-05-11", event: "Post-operative complication discovered", sourceDocId: "doc_001", sourceDocName: "Martinez Medical Records", pageReference: "78", confirmed: false },
      { id: "kd5", date: "2023-06-30", event: "Revision surgery performed", sourceDocId: "doc_001", sourceDocName: "Martinez Medical Records", pageReference: "102", confirmed: true },
    ],
    disputedFacts: [
      { id: "df1", description: "Whether Dr. Patel reviewed the MRI images before proceeding with surgery", sourceDocId: "doc_002", pageReference: "23-25", status: "disputed" },
      { id: "df2", description: "Whether nursing staff alerted Dr. Patel to abnormal vitals during the procedure", sourceDocId: "doc_003", pageReference: "4", status: "disputed" },
    ],
    priorStatements: [
      { id: "ps1", witnessName: "Dr. Rajesh Patel", date: "2024-01-15", sourceDocId: "doc_002", summary: "Stated he reviewed all imaging prior to surgery and found no contraindications", pageReference: "14-18" },
      { id: "ps2", witnessName: "Dr. Rajesh Patel", date: "2024-01-15", sourceDocId: "doc_002", summary: "Acknowledged the post-operative complication but attributed it to patient anatomy, not surgical error", pageReference: "42-47" },
    ],
    allConfirmed: false,
  },
};

// ---- Briefs ----
const makeBrief = (id: string, sessionId: string, caseId: string, witnessName: string, score: number, delta: number): Brief => ({
  id,
  sessionId,
  caseId,
  witnessName,
  sessionScore: score,
  deltaFromFirst: delta,
  consistencyRate: Math.min(95, 60 + score * 0.4),
  alertTotals: { objections: Math.floor(Math.random() * 5) + 1, inconsistencies: Math.floor(Math.random() * 4) + 1, behavioral: Math.floor(Math.random() * 3) },
  inconsistencies: [
    {
      id: `${id}_inc1`,
      timestamp: 420,
      highlightedPhrase: "I always review imaging before any surgical procedure",
      priorStatementQuote: "I don't always have time to review every scan personally before we begin",
      priorSource: "Prior Deposition",
      priorPageLine: "p.23 ln.4-7",
      confidenceScore: 0.89,
      impeachmentRisk: "high",
      coachNote: "Direct contradiction on standard of care. Prepare witness to reconcile these statements or clarify context.",
      confirmed: true,
    },
    {
      id: `${id}_inc2`,
      timestamp: 780,
      highlightedPhrase: "The nursing staff never raised any concerns during the procedure",
      priorStatementQuote: "I recall Nurse Okafor mentioning something about the vitals, but I was focused on the procedure",
      priorSource: "Prior Deposition",
      priorPageLine: "p.45 ln.12-15",
      confidenceScore: 0.76,
      impeachmentRisk: "medium",
      coachNote: "Witness may have forgotten prior acknowledgment. Coach on consistency regarding nursing communications.",
      confirmed: true,
    },
  ],
  objections: [
    { id: `${id}_obj1`, timestamp: 310, questionText: "Isn't it true that you were negligent in failing to review the MRI?", freRule: "FRE 611(a)", trainingNote: "Leading and argumentative. Coach witness to wait for objection before answering compound questions.", objectionRate: 0.85 },
    { id: `${id}_obj2`, timestamp: 650, questionText: "How do you explain the hospital records contradicting your testimony?", freRule: "FRE 803(6)", trainingNote: "Assumes facts not in evidence. Train witness to ask for specific document references.", objectionRate: 0.72 },
  ],
  weaknessMap: {
    timeline: Math.min(100, 40 + score * 0.6),
    financial: Math.min(100, 30 + score * 0.5),
    communications: Math.min(100, 35 + score * 0.55),
    relationships: Math.min(100, 50 + score * 0.4),
    actions: Math.min(100, 45 + score * 0.5),
    priorStatements: Math.min(100, 25 + score * 0.6),
    composure: Math.min(100, 55 + score * 0.35),
  },
  recommendations: [
    "Practice timeline consistency: Rehearse the sequence of events from initial consultation through revision surgery with precise dates.",
    "Address prior statement contradictions: Prepare clear explanations for discrepancies between current testimony and prior deposition statements.",
    "Improve composure under pressure: Focus on pausing before answering aggressive or compound questions.",
  ],
  coachNarrationUrl: "/mock-narration.mp3",
  createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
});

export const MOCK_BRIEFS: Record<string, Brief[]> = {
  case_001: [
    makeBrief("brief_004", "ses_004", "case_001", "Dr. Rajesh Patel", 72, 27),
    makeBrief("brief_003", "ses_003", "case_001", "Dr. Rajesh Patel", 66, 21),
    makeBrief("brief_002", "ses_002", "case_001", "Dr. Rajesh Patel", 58, 13),
    makeBrief("brief_001", "ses_001", "case_001", "Dr. Rajesh Patel", 45, 0),
    makeBrief("brief_005", "ses_005", "case_001", "Nurse Linda Okafor", 52, 0),
    makeBrief("brief_006", "ses_006", "case_001", "Nurse Linda Okafor", 61, 9),
    makeBrief("brief_007", "ses_007", "case_001", "Carlos Martinez", 38, 0),
  ],
  case_002: [
    makeBrief("brief_012", "ses_012", "case_002", "David Thompson", 68, 27),
    makeBrief("brief_011", "ses_011", "case_002", "David Thompson", 55, 14),
    makeBrief("brief_010", "ses_010", "case_002", "David Thompson", 41, 0),
    makeBrief("brief_013", "ses_013", "case_002", "Karen Miller", 54, 0),
  ],
  case_003: [
    makeBrief("brief_020", "ses_020", "case_003", "Frank Greenfield", 47, 0),
  ],
};

// Flat brief lookup
export const ALL_BRIEFS: Brief[] = Object.values(MOCK_BRIEFS).flat();

// ---- Session Lobby ----
export const getMockLobby = (caseId: string, sessionId: string): SessionLobby | null => {
  const sessions = MOCK_SESSIONS[caseId];
  const session = sessions?.find(s => s.id === sessionId);
  if (!session) return null;
  const caseName = MOCK_CASES.find(c => c.id === caseId)?.name || "Unknown Case";
  return {
    session,
    caseName,
    witnessConnected: true,
    documentsIndexed: MOCK_DOCUMENTS[caseId]?.filter(d => d.status === "ready").length || 0,
    priorSessionCount: sessions.filter(s => s.witnessId === session.witnessId && s.id !== sessionId).length,
    practiceLink: `${window.location.origin}/witness/session/${sessionId}?token=mock-witness-token`,
  };
};

// ---- Live Session State (demo) ----
export const MOCK_LIVE_SESSION: LiveSessionState = {
  status: "active",
  elapsedSeconds: 847,
  totalSeconds: 1800,
  currentTopic: "Timeline of Events",
  questionCount: 14,
  transcript: [
    { id: "t1", speaker: "system", text: "Session started. Interrogator: Nia (AI). Witness: Dr. Rajesh Patel.", timestamp: 0, flagged: false },
    { id: "t2", speaker: "interrogator", text: "Dr. Patel, let's begin with the timeline. When did you first see Mr. Martinez as a patient?", timestamp: 15, flagged: false },
    { id: "t3", speaker: "witness", text: "I first saw Mr. Martinez on March 15th, 2023 for an initial consultation regarding his back pain.", timestamp: 28, flagged: false },
    { id: "t4", speaker: "interrogator", text: "And who referred Mr. Martinez to you?", timestamp: 45, flagged: false },
    { id: "t5", speaker: "witness", text: "He was referred by his primary care physician, Dr. Williams.", timestamp: 58, flagged: false },
    { id: "t6", speaker: "interrogator", text: "Before performing the spinal fusion surgery, did you personally review the MRI images?", timestamp: 120, flagged: false },
    { id: "t7", speaker: "witness", text: "Yes, I always review imaging before any surgical procedure. It's my standard practice.", timestamp: 138, flagged: true },
    { id: "t8", speaker: "interrogator", text: "Isn't it true that you were negligent in failing to adequately review the MRI?", timestamp: 310, flagged: true },
    { id: "t9", speaker: "witness", text: "No, that's absolutely not true. I reviewed all the imaging thoroughly.", timestamp: 325, flagged: false },
    { id: "t10", speaker: "interrogator", text: "Let me direct your attention to your prior deposition, page 23, lines 4 through 7. You stated, and I quote: 'I don't always have time to review every scan personally before we begin.' How do you reconcile that with your testimony today?", timestamp: 400, flagged: true },
    { id: "t11", speaker: "witness", text: "I... that was referring to routine follow-up imaging, not pre-operative imaging. Those are completely different situations.", timestamp: 420, flagged: true },
    { id: "t12", speaker: "interrogator", text: "During the surgery on May 10th, did the nursing staff raise any concerns about Mr. Martinez's vitals?", timestamp: 600, flagged: false },
    { id: "t13", speaker: "witness", text: "The nursing staff never raised any concerns during the procedure. Everything was proceeding normally.", timestamp: 618, flagged: true },
    { id: "t14", speaker: "interrogator", text: "But in your prior deposition at page 45, you stated that Nurse Okafor mentioned something about the vitals. Were you not being truthful then, or are you not being truthful now?", timestamp: 780, flagged: true },
  ],
  alerts: [
    {
      id: "alert_001", type: "inconsistency", severity: "critical", timestamp: 420,
      title: "Statement Contradiction Detected",
      description: "Witness claims to 'always review imaging' but prior deposition states otherwise.",
      confidenceScore: 0.89,
      priorQuote: "I don't always have time to review every scan personally before we begin",
      priorSource: "Prior Deposition",
      priorPageLine: "p.23 ln.4-7",
      status: "pending",
    },
    {
      id: "alert_002", type: "objection", severity: "critical", timestamp: 310,
      title: "Objectionable Question",
      description: "Leading and argumentative question assuming negligence.",
      freRule: "FRE 611(a)",
      status: "confirmed",
    },
    {
      id: "alert_003", type: "inconsistency", severity: "warning", timestamp: 780,
      title: "Nursing Communication Contradiction",
      description: "Witness denies nursing concerns but prior testimony acknowledges them.",
      confidenceScore: 0.76,
      priorQuote: "I recall Nurse Okafor mentioning something about the vitals",
      priorSource: "Prior Deposition",
      priorPageLine: "p.45 ln.12-15",
      status: "pending",
    },
    {
      id: "alert_004", type: "behavioral", severity: "info", timestamp: 420,
      title: "Stress Indicator",
      description: "Elevated micro-expression activity detected during MRI review discussion.",
      auCodes: ["AU1", "AU4", "AU15"],
      experimentalLabel: true,
      status: "pending",
    },
  ],
  witnessConnected: true,
  serviceStatus: { elevenlabs: true, nemotron: true, nia: true },
};

// ---- Settings ----
export const MOCK_SETTINGS: AttorneySettings = {
  profile: { name: "Sarah Chen", email: "sarah.chen@morrison-associates.com", title: "Senior Litigation Partner", practiceArea: "Medical Malpractice", ssoManaged: false },
  sessionDefaults: { durationMinutes: 30, aggressionLevel: "standard", objectionCopilotDefault: true },
  notifications: { briefReady: true, plateauAlert: true, sessionReminder: true },
};

export const MOCK_ACTIVE_SESSIONS: ActiveSession[] = [
  { id: "as_1", device: "Chrome on MacBook Pro", ipAddress: "192.168.1.42", lastActive: "Just now", current: true },
  { id: "as_2", device: "Safari on iPhone 15", ipAddress: "192.168.1.43", lastActive: "2 hours ago", current: false },
];

// ---- Brief Generation Status ----
export const MOCK_BRIEF_STATUS = {
  progress: 100,
  eta: 0,
  briefId: "brief_004",
};
