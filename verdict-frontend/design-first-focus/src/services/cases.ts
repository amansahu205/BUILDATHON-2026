import { MOCK_CASES, MOCK_DOCUMENTS, MOCK_FACT_REVIEWS } from "@/mocks/data";
import type { Case, CaseDocument, CreateCaseRequest, FactReview, PaginatedResponse } from "@/types";

export const casesService = {
  list: async (params?: { page?: number; search?: string }): Promise<PaginatedResponse<Case>> => {
    let cases = [...MOCK_CASES];
    if (params?.search) {
      const q = params.search.toLowerCase();
      cases = cases.filter(c => c.name.toLowerCase().includes(q));
    }
    return { data: cases, total: cases.length, page: params?.page || 1, pageSize: 20 };
  },

  get: async (caseId: string): Promise<Case> => {
    const c = MOCK_CASES.find(c => c.id === caseId);
    if (!c) throw new Error("Case not found");
    return c;
  },

  create: async (payload: CreateCaseRequest): Promise<Case> => {
    const newCase: Case = {
      id: `case_${Date.now()}`,
      ...payload,
      witnessCount: 0,
      documentCount: 0,
      sessionCount: 0,
      status: "active",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    MOCK_CASES.push(newCase);
    return newCase;
  },

  getDocuments: async (caseId: string): Promise<CaseDocument[]> => {
    return MOCK_DOCUMENTS[caseId] || [];
  },

  uploadDocument: async (
    _caseId: string,
    _file: File,
    _type: string,
    onProgress?: (pct: number) => void,
  ): Promise<CaseDocument> => {
    for (let i = 0; i <= 100; i += 20) {
      await new Promise(r => setTimeout(r, 200));
      onProgress?.(i);
    }
    return {
      id: `doc_${Date.now()}`,
      caseId: _caseId,
      fileName: _file.name,
      fileSize: _file.size,
      mimeType: _file.type,
      status: "indexing",
      documentType: "other",
      uploadedAt: new Date().toISOString(),
    };
  },

  getFactReview: async (caseId: string): Promise<FactReview> => {
    return MOCK_FACT_REVIEWS[caseId] || {
      parties: [],
      keyDates: [],
      disputedFacts: [],
      priorStatements: [],
      allConfirmed: false,
    };
  },
};
