import { api } from "./api";
import type { Witness, CreateWitnessRequest } from "@/types";

export const witnessesService = {
  list: async (caseId: string): Promise<Witness[]> => {
    try {
      const { data: resp } = await api.get(`/cases/${caseId}/witnesses`);
      const witnesses = resp.data?.witnesses ?? resp.data ?? [];
      return Array.isArray(witnesses) ? witnesses.map(mapWitness) : [];
    } catch {
      return [];
    }
  },

  get: async (caseId: string, witnessId: string): Promise<Witness> => {
    const { data: resp } = await api.get(`/cases/${caseId}/witnesses/${witnessId}`);
    return mapWitness(resp.data);
  },

  create: async (caseId: string, payload: CreateWitnessRequest): Promise<Witness> => {
    const { data: resp } = await api.post(`/cases/${caseId}/witnesses`, {
      name: payload.name,
      role: payload.role.toUpperCase(),
      email: `${payload.name.toLowerCase().replace(/\s+/g, ".")}@witness.verdict.law`,
    });
    return mapWitness(resp.data);
  },
};

function mapWitness(raw: Record<string, unknown>): Witness {
  return {
    id: raw.id as string,
    caseId: raw.caseId as string ?? "",
    name: raw.name as string,
    role: (raw.role as string ?? "").toLowerCase(),
    sessionCount: (raw.sessionCount as number) ?? 0,
    latestScore: raw.latestScore as number | undefined,
    scoreTrend: [],
    plateauAlert: (raw.plateauDetected as boolean) ?? false,
    createdAt: raw.createdAt as string ?? new Date().toISOString(),
  };
}
