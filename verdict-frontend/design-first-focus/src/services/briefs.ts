import { MOCK_BRIEFS, ALL_BRIEFS, MOCK_BRIEF_STATUS } from "@/mocks/data";
import type { Brief } from "@/types";

export const briefsService = {
  list: async (caseId: string): Promise<Brief[]> => {
    return MOCK_BRIEFS[caseId] || [];
  },

  get: async (briefId: string): Promise<Brief> => {
    const brief = ALL_BRIEFS.find(b => b.id === briefId);
    if (!brief) throw new Error("Brief not found");
    return brief;
  },

  getGenerationStatus: async (_sessionId: string): Promise<{ progress: number; eta: number; briefId?: string }> => {
    return MOCK_BRIEF_STATUS;
  },

  downloadPdf: async (_briefId: string): Promise<Blob> => {
    return new Blob(["Mock PDF content"], { type: "application/pdf" });
  },

  shareWithWitness: async (_briefId: string): Promise<void> => {},
};
