// ============================================================
// VERDICT — Shared TypeScript types (API-only, no mocks)
// ============================================================

// ---- Auth ----
export interface User {
  id: string;
  email: string;
  name: string;
  role: "attorney" | "admin" | "witness";
  firmId: string;
  title?: string;
  practiceArea?: string;
  avatarUrl?: string;
  ssoEnabled: boolean;
  createdAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

// ---- Firm ----
export interface Firm {
  id: string;
  name: string;
  ssoEnabled: boolean;
  retentionDays: number;
  caseIsolation: boolean;
  behavioralSentinelEnabled: boolean;
  seatsTotal: number;
  seatsUsed: number;
  plan: string;
  createdAt: string;
}

export interface FirmOnboardingPayload {
  firmName: string;
  adminName: string;
  adminEmail: string;
  ssoEnabled: boolean;
  passwordPolicy?: string;
  seats: SeatProvision[];
  retentionDays: number;
  caseIsolation: boolean;
  behavioralSentinel: boolean;
}

export interface SeatProvision {
  email: string;
  name: string;
  role: "attorney" | "admin";
}

// ---- Cases ----
export type CaseType =
  | "medical_malpractice"
  | "employment_discrimination"
  | "personal_injury"
  | "commercial_litigation"
  | "product_liability"
  | "intellectual_property"
  | "securities_fraud"
  | "environmental"
  | "other";

export const CASE_TYPE_LABELS: Record<CaseType, string> = {
  medical_malpractice: "Medical Malpractice",
  employment_discrimination: "Employment Discrimination",
  personal_injury: "Personal Injury",
  commercial_litigation: "Commercial Litigation",
  product_liability: "Product Liability",
  intellectual_property: "Intellectual Property",
  securities_fraud: "Securities Fraud",
  environmental: "Environmental",
  other: "Other",
};

export interface Case {
  id: string;
  name: string;
  caseType: CaseType;
  opposingFirm?: string;
  depositionDate: string;
  witnessCount: number;
  documentCount: number;
  sessionCount: number;
  status: "active" | "archived";
  createdAt: string;
  updatedAt: string;
}

export interface CreateCaseRequest {
  name: string;
  caseType: CaseType;
  opposingFirm?: string;
  depositionDate: string;
}

// ---- Documents ----
export type DocumentStatus = "uploading" | "indexing" | "ready" | "failed";
export type DocumentType = "medical_record" | "deposition" | "pleading" | "exhibit" | "correspondence" | "expert_report" | "other";

export interface CaseDocument {
  id: string;
  caseId: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
  status: DocumentStatus;
  documentType: DocumentType;
  pageCount?: number;
  uploadedAt: string;
  indexedAt?: string;
  error?: string;
}

// ---- Facts ----
export interface Party {
  id: string;
  name: string;
  role: string;
  description?: string;
  confirmed: boolean;
}

export interface KeyDate {
  id: string;
  date: string;
  event: string;
  sourceDocId: string;
  sourceDocName: string;
  pageReference: string;
  confirmed: boolean;
}

export interface DisputedFact {
  id: string;
  description: string;
  sourceDocId: string;
  pageReference: string;
  status: "disputed" | "confirmed" | "resolved";
}

export interface PriorStatement {
  id: string;
  witnessName: string;
  date: string;
  sourceDocId: string;
  summary: string;
  pageReference: string;
}

export interface FactReview {
  parties: Party[];
  keyDates: KeyDate[];
  disputedFacts: DisputedFact[];
  priorStatements: PriorStatement[];
  allConfirmed: boolean;
}

// ---- Witnesses ----
export interface Witness {
  id: string;
  caseId: string;
  name: string;
  role: string;
  sessionCount: number;
  latestScore?: number;
  scoreTrend: number[];
  plateauAlert: boolean;
  createdAt: string;
}

export interface CreateWitnessRequest {
  name: string;
  role: string;
}

// ---- Sessions ----
export type FocusArea = "timeline" | "financial" | "communications" | "relationships" | "actions" | "prior_statements";
export type AggressionLevel = "standard" | "elevated" | "high_stakes";
export type SessionStatus = "configuring" | "lobby" | "connecting" | "active" | "paused" | "witness_disconnected" | "ending" | "complete";

export const FOCUS_AREA_LABELS: Record<FocusArea, string> = {
  timeline: "Timeline",
  financial: "Financial",
  communications: "Communications",
  relationships: "Relationships",
  actions: "Actions",
  prior_statements: "Prior Statements",
};

export interface SessionConfig {
  witnessId: string;
  durationMinutes: 15 | 30 | 45 | 60;
  focusAreas: FocusArea[];
  aggressionLevel: AggressionLevel;
  objectionCopilot: boolean;
  behavioralSentinel: boolean;
}

export interface Session {
  id: string;
  caseId: string;
  witnessId: string;
  witnessName: string;
  config: SessionConfig;
  status: SessionStatus;
  score?: number;
  briefId?: string;
  startedAt?: string;
  endedAt?: string;
  createdAt: string;
}

export interface SessionLobby {
  session: Session;
  caseName: string;
  witnessConnected: boolean;
  documentsIndexed: number;
  priorSessionCount: number;
  practiceLink: string;
}

// ---- Live Session ----
export interface TranscriptEntry {
  id: string;
  speaker: "interrogator" | "witness" | "attorney" | "system";
  text: string;
  timestamp: number;
  flagged: boolean;
}

export type AlertType = "objection" | "inconsistency" | "behavioral";
export type AlertSeverity = "critical" | "warning" | "info";

export interface LiveAlert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  timestamp: number;
  title: string;
  description: string;
  // Objection-specific
  freRule?: string;
  // Inconsistency-specific
  confidenceScore?: number;
  priorQuote?: string;
  priorSource?: string;
  priorPageLine?: string;
  // Behavioral-specific
  auCodes?: string[];
  experimentalLabel?: boolean;
  // Actions
  status: "pending" | "confirmed" | "rejected" | "dismissed" | "annotated";
  annotation?: string;
}

export interface LiveSessionState {
  status: SessionStatus;
  elapsedSeconds: number;
  totalSeconds: number;
  currentTopic: string;
  questionCount: number;
  transcript: TranscriptEntry[];
  alerts: LiveAlert[];
  witnessConnected: boolean;
  serviceStatus: {
    elevenlabs: boolean;
    nemotron: boolean;
    nia: boolean;
  };
}

// ---- Briefs ----
export interface Brief {
  id: string;
  sessionId: string;
  caseId: string;
  witnessName: string;
  sessionScore: number;
  deltaFromFirst: number;
  consistencyRate: number;
  alertTotals: {
    objections: number;
    inconsistencies: number;
    behavioral: number;
  };
  inconsistencies: BriefInconsistency[];
  objections: BriefObjection[];
  weaknessMap: WeaknessMap;
  recommendations: string[];
  coachNarrationUrl?: string;
  createdAt: string;
}

export interface BriefInconsistency {
  id: string;
  timestamp: number;
  highlightedPhrase: string;
  priorStatementQuote: string;
  priorSource: string;
  priorPageLine: string;
  confidenceScore: number;
  impeachmentRisk: "high" | "medium" | "low";
  coachNote: string;
  audioTimestamp?: number;
  confirmed: boolean;
}

export interface BriefObjection {
  id: string;
  timestamp: number;
  questionText: string;
  freRule: string;
  trainingNote: string;
  objectionRate: number;
}

export interface WeaknessMap {
  timeline: number;
  financial: number;
  communications: number;
  relationships: number;
  actions: number;
  priorStatements: number;
  composure?: number;
}

// ---- Settings ----
export interface AttorneySettings {
  profile: {
    name: string;
    email: string;
    title: string;
    practiceArea: string;
    ssoManaged: boolean;
  };
  sessionDefaults: {
    durationMinutes: 15 | 30 | 45 | 60;
    aggressionLevel: AggressionLevel;
    objectionCopilotDefault: boolean;
  };
  notifications: {
    briefReady: boolean;
    plateauAlert: boolean;
    sessionReminder: boolean;
  };
}

export interface ActiveSession {
  id: string;
  device: string;
  ipAddress: string;
  lastActive: string;
  current: boolean;
}

// ---- Admin (static mockup types) ----
export interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: "attorney" | "admin";
  status: "active" | "pending" | "deactivated";
  lastActive?: string;
  sessionsRun: number;
}

export interface AdminAnalytics {
  totalSessions: number;
  totalWitnesses: number;
  averageScore: number;
  scoresByAttorney: { name: string; avgScore: number; sessions: number }[];
  sessionsByMonth: { month: string; count: number }[];
}

// ---- API Response wrappers ----
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ApiError {
  message: string;
  code: string;
  statusCode: number;
}
