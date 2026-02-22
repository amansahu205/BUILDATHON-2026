import { api } from "./api";
import type { Brief } from "@/types";

export const briefsService = {
  list: async (caseId: string): Promise<Brief[]> => {
    try {
      const { data: resp } = await api.get(`/briefs/`, { params: { caseId } });
      const briefs = resp.data?.briefs ?? resp.data ?? [];
      return Array.isArray(briefs) ? briefs.map(mapBrief) : [];
    } catch {
      return [];
    }
  },

  get: async (briefId: string): Promise<Brief> => {
    const { data: resp } = await api.get(`/briefs/${briefId}`);
    return mapBrief(resp.data);
  },

  getGenerationStatus: async (sessionId: string): Promise<{ progress: number; eta: number; briefId?: string }> => {
    try {
      const { data: resp } = await api.get(`/briefs/generate/${sessionId}/status`);
      return resp.data;
    } catch {
      return { progress: 100, eta: 0 };
    }
  },

  downloadPdf: async (briefId: string): Promise<Blob> => {
    const { data: resp } = await api.get(`/briefs/${briefId}/pdf`);
    const downloadUrl = resp.data?.downloadUrl;
    if (downloadUrl) {
      const pdfResp = await fetch(downloadUrl);
      return pdfResp.blob();
    }
    return new Blob(["PDF unavailable"], { type: "text/plain" });
  },

  shareWithWitness: async (briefId: string): Promise<void> => {
    await api.post(`/briefs/${briefId}/share`);
  },
};

function mapBrief(raw: Record<string, unknown>): Brief {
  const weaknessMap = (raw.weaknessMapScores ?? raw.weaknessMap ?? {}) as Record<string, number>;
  const recommendations = (raw.topRecommendations ?? raw.recommendations ?? []) as string[];

  return {
    id: raw.id as string,
    sessionId: raw.sessionId as string ?? "",
    caseId: raw.caseId as string ?? "",
    witnessName: raw.witnessName as string ?? "",
    sessionScore: (raw.sessionScore as number) ?? 0,
    deltaFromFirst: (raw.deltaVsBaseline as number) ?? 0,
    consistencyRate: (raw.consistencyRate as number) ?? 0,
    alertTotals: {
      objections: (raw.objectionCount as number) ?? 0,
      inconsistencies: (raw.confirmedFlags as number) ?? 0,
      behavioral: (raw.composureAlerts as number) ?? 0,
    },
    inconsistencies: [],
    objections: [],
    weaknessMap: {
      timeline: weaknessMap.tactical_discipline ?? 0,
      financial: weaknessMap.directness ?? 0,
      communications: weaknessMap.professionalism ?? 0,
      relationships: weaknessMap.consistency ?? 0,
      actions: weaknessMap.composure ?? 0,
      priorStatements: 0,
      composure: weaknessMap.composure ?? 0,
    },
    recommendations,
    createdAt: raw.createdAt as string ?? new Date().toISOString(),
  };
}
