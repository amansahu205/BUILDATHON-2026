import { MOCK_WITNESSES } from "@/mocks/data";
import type { Witness, CreateWitnessRequest } from "@/types";

export const witnessesService = {
  list: async (caseId: string): Promise<Witness[]> => {
    return MOCK_WITNESSES[caseId] || [];
  },

  get: async (caseId: string, witnessId: string): Promise<Witness> => {
    const witness = MOCK_WITNESSES[caseId]?.find(w => w.id === witnessId);
    if (!witness) throw new Error("Witness not found");
    return witness;
  },

  create: async (caseId: string, payload: CreateWitnessRequest): Promise<Witness> => {
    const newWitness: Witness = {
      id: `wit_${Date.now()}`,
      caseId,
      name: payload.name,
      role: payload.role,
      sessionCount: 0,
      scoreTrend: [],
      plateauAlert: false,
      createdAt: new Date().toISOString(),
    };
    if (!MOCK_WITNESSES[caseId]) MOCK_WITNESSES[caseId] = [];
    MOCK_WITNESSES[caseId].push(newWitness);
    return newWitness;
  },
};
