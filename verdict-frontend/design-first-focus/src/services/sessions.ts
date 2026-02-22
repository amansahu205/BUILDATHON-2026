import { api } from "./api";
import type { Session, SessionConfig, SessionLobby, LiveSessionState } from "@/types";

export const sessionsService = {
  list: async (caseId: string): Promise<Session[]> => {
    try {
      const { data: resp } = await api.get(`/sessions/`, { params: { caseId } });
      const sessions = resp.data?.sessions ?? resp.data ?? [];
      return Array.isArray(sessions) ? sessions.map(mapSession) : [];
    } catch {
      return [];
    }
  },

  get: async (_caseId: string, sessionId: string): Promise<Session> => {
    const { data: resp } = await api.get(`/sessions/${sessionId}`);
    return mapSession(resp.data);
  },

  create: async (caseId: string, config: SessionConfig): Promise<Session> => {
    const { data: resp } = await api.post("/sessions/", {
      caseId,
      witnessId: config.witnessId,
      durationMinutes: config.durationMinutes,
      aggression: config.aggressionLevel.toUpperCase(),
      focusAreas: config.focusAreas,
    });
    return {
      id: resp.data.id,
      caseId,
      witnessId: config.witnessId,
      witnessName: "",
      config,
      status: "lobby",
      createdAt: new Date().toISOString(),
    };
  },

  getLobby: async (caseId: string, sessionId: string): Promise<SessionLobby> => {
    const session = await sessionsService.get(caseId, sessionId);
    return {
      session,
      caseName: "",
      witnessConnected: false,
      documentsIndexed: 0,
      priorSessionCount: 0,
      practiceLink: "",
    };
  },

  start: async (_caseId: string, sessionId: string): Promise<void> => {
    await api.post(`/sessions/${sessionId}/start`);
  },

  pause: async (_caseId: string, sessionId: string): Promise<void> => {
    await api.post(`/sessions/${sessionId}/pause`);
  },

  resume: async (_caseId: string, sessionId: string): Promise<void> => {
    await api.post(`/sessions/${sessionId}/resume`);
  },

  end: async (_caseId: string, sessionId: string): Promise<void> => {
    await api.post(`/sessions/${sessionId}/end`);
  },

  skipTopic: async (_caseId: string, _sessionId: string): Promise<void> => {},
  addNote: async (_caseId: string, _sessionId: string, _note: string): Promise<void> => {},

  getLiveState: async (sessionId: string): Promise<LiveSessionState> => {
    const { data: resp } = await api.get(`/sessions/${sessionId}/live-state`);
    return resp.data as LiveSessionState;
  },

  uploadAnswerAudio: async (
    sessionId: string,
    blob: Blob,
    questionNumber: number,
    durationMs: number,
  ): Promise<{ transcriptText: string }> => {
    const fd = new FormData();
    fd.append("file", new File([blob], `answer-${Date.now()}.webm`, { type: blob.type || "audio/webm" }));
    fd.append("questionNumber", String(questionNumber));
    fd.append("durationMs", String(durationMs));
    const { data: resp } = await api.post(`/sessions/${sessionId}/answers/audio`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return resp.data as { transcriptText: string };
  },

  streamQuestion: async (
    sessionId: string,
    payload: {
      questionNumber: number;
      priorAnswer?: string;
      hesitationDetected?: boolean;
      recentInconsistencyFlag?: boolean;
      currentTopic?: string;
    },
    onEvent: (event: { type: string; [key: string]: unknown }) => void,
  ): Promise<void> => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:4000/api/v1";
    const tokens = localStorage.getItem("verdict_access_token");
    const res = await fetch(`${baseUrl}/sessions/${sessionId}/agents/question`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(tokens ? { Authorization: `Bearer ${tokens}` } : {}),
      },
      body: JSON.stringify({
        questionNumber: payload.questionNumber,
        priorAnswer: payload.priorAnswer ?? null,
        hesitationDetected: payload.hesitationDetected ?? false,
        recentInconsistencyFlag: payload.recentInconsistencyFlag ?? false,
        currentTopic: payload.currentTopic ?? "PRIOR_STATEMENTS",
      }),
    });
    if (!res.ok || !res.body) {
      throw new Error("Failed to stream question");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";
      for (const part of parts) {
        const line = part.split("\n").find((l) => l.startsWith("data: "));
        if (!line) continue;
        try {
          onEvent(JSON.parse(line.slice(6)));
        } catch {
          // ignore malformed chunks
        }
      }
    }
  },

  getWitnessSession: async (sessionId: string, _token: string): Promise<Session> => {
    const { data: resp } = await api.get(`/sessions/${sessionId}`);
    return mapSession(resp.data);
  },
};

function mapSession(raw: Record<string, unknown>): Session {
  return {
    id: raw.id as string,
    caseId: raw.caseId as string ?? "",
    witnessId: raw.witnessId as string ?? "",
    witnessName: raw.witnessName as string ?? "",
    config: {
      witnessId: raw.witnessId as string ?? "",
      durationMinutes: (raw.durationMinutes as 15 | 30 | 45 | 60) ?? 30,
      focusAreas: (raw.focusAreas as string[]) ?? [],
      aggressionLevel: ((raw.aggression as string) ?? "standard").toLowerCase() as "standard" | "elevated" | "high_stakes",
      objectionCopilot: (raw.objectionCopilotEnabled as boolean) ?? true,
      behavioralSentinel: (raw.sentinelEnabled as boolean) ?? false,
    },
    status: ((raw.status as string) ?? "lobby").toLowerCase() as Session["status"],
    score: raw.sessionScore as number | undefined,
    startedAt: raw.startedAt as string | undefined,
    endedAt: raw.endedAt as string | undefined,
    createdAt: raw.createdAt as string ?? new Date().toISOString(),
  };
}
