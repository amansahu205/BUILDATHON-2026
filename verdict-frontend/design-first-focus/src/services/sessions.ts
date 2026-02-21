import { MOCK_SESSIONS, getMockLobby } from "@/mocks/data";
import type { Session, SessionConfig, SessionLobby } from "@/types";

export const sessionsService = {
  list: async (caseId: string): Promise<Session[]> => {
    return MOCK_SESSIONS[caseId] || [];
  },

  get: async (caseId: string, sessionId: string): Promise<Session> => {
    const session = MOCK_SESSIONS[caseId]?.find(s => s.id === sessionId);
    if (!session) throw new Error("Session not found");
    return session;
  },

  create: async (caseId: string, config: SessionConfig): Promise<Session> => {
    const witnessName = "Mock Witness";
    const newSession: Session = {
      id: `ses_${Date.now()}`,
      caseId,
      witnessId: config.witnessId,
      witnessName,
      config,
      status: "lobby",
      createdAt: new Date().toISOString(),
    };
    if (!MOCK_SESSIONS[caseId]) MOCK_SESSIONS[caseId] = [];
    MOCK_SESSIONS[caseId].push(newSession);
    return newSession;
  },

  getLobby: async (caseId: string, sessionId: string): Promise<SessionLobby> => {
    const lobby = getMockLobby(caseId, sessionId);
    if (!lobby) throw new Error("Lobby not found");
    return lobby;
  },

  start: async (_caseId: string, _sessionId: string, _withoutWitness?: boolean): Promise<void> => {},
  pause: async (_caseId: string, _sessionId: string): Promise<void> => {},
  resume: async (_caseId: string, _sessionId: string): Promise<void> => {},
  end: async (_caseId: string, _sessionId: string): Promise<void> => {},
  skipTopic: async (_caseId: string, _sessionId: string): Promise<void> => {},
  addNote: async (_caseId: string, _sessionId: string, _note: string): Promise<void> => {},

  getWitnessSession: async (sessionId: string, _token: string): Promise<Session> => {
    for (const sessions of Object.values(MOCK_SESSIONS)) {
      const s = sessions.find(s => s.id === sessionId);
      if (s) return s;
    }
    throw new Error("Session not found");
  },
};
