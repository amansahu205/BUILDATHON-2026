import { api } from "./api";
import type { Case, CaseDocument, CreateCaseRequest, FactReview, PaginatedResponse } from "@/types";

export const casesService = {
  list: async (params?: { page?: number; search?: string }): Promise<PaginatedResponse<Case>> => {
    const { data: resp } = await api.get("/cases/", { params });
    const cases: Case[] = (resp.data?.cases ?? []).map(mapCase);
    return {
      data: cases,
      total: resp.data?.pagination?.total ?? cases.length,
      page: resp.data?.pagination?.page ?? params?.page ?? 1,
      pageSize: resp.data?.pagination?.limit ?? 20,
    };
  },

  get: async (caseId: string): Promise<Case> => {
    const { data: resp } = await api.get(`/cases/${caseId}`);
    return mapCase(resp.data);
  },

  create: async (payload: CreateCaseRequest): Promise<Case> => {
    const { data: resp } = await api.post("/cases/", {
      caseName: payload.name,
      caseType: mapCaseTypeToBackend(payload.caseType),
      opposingParty: payload.opposingFirm,
      depositionDate: payload.depositionDate,
    });
    return mapCase(resp.data);
  },

  getDocuments: async (caseId: string): Promise<CaseDocument[]> => {
    const { data: resp } = await api.get(`/cases/${caseId}/documents`);
    return (resp.data?.documents ?? []).map(mapDocument);
  },

  uploadDocument: async (
    caseId: string,
    file: File,
    docType: string,
    onProgress?: (pct: number) => void,
  ): Promise<CaseDocument> => {
    const backendDocType = mapDocTypeToBackend(docType);

    onProgress?.(10);
    const { data: presignResp } = await api.post(`/cases/${caseId}/documents/upload`, {
      filename: file.name,
      mimeType: file.type || "application/octet-stream",
      fileSizeBytes: file.size,
      docType: backendDocType,
    });

    const { documentId, uploadUrl } = presignResp.data;
    onProgress?.(30);

    await fetch(uploadUrl, {
      method: "PUT",
      headers: { "Content-Type": file.type || "application/octet-stream" },
      body: file,
    });
    onProgress?.(70);

    await api.post(`/cases/${caseId}/documents/${documentId}/confirm`);
    onProgress?.(100);

    return {
      id: documentId,
      caseId,
      fileName: file.name,
      fileSize: file.size,
      mimeType: file.type,
      status: "indexing",
      documentType: docType as CaseDocument["documentType"],
      uploadedAt: new Date().toISOString(),
    };
  },

  getFactReview: async (caseId: string): Promise<FactReview> => {
    const { data: resp } = await api.get(`/cases/${caseId}/facts`);
    return {
      parties: resp.data?.parties ?? [],
      keyDates: resp.data?.keyDates ?? [],
      disputedFacts: resp.data?.disputedFacts ?? [],
      priorStatements: resp.data?.priorStatements ?? [],
      allConfirmed: resp.data?.allConfirmed ?? false,
    };
  },
};

function mapCaseTypeToBackend(frontendType: string): string {
  const map: Record<string, string> = {
    medical_malpractice: "MEDICAL_MALPRACTICE",
    employment_discrimination: "EMPLOYMENT_DISCRIMINATION",
    commercial_litigation: "COMMERCIAL_DISPUTE",
    personal_injury: "OTHER",
    product_liability: "OTHER",
    intellectual_property: "OTHER",
    securities_fraud: "OTHER",
    environmental: "OTHER",
    other: "OTHER",
  };
  return map[frontendType] || "OTHER";
}

function mapCaseTypeToFrontend(backendType: string): Case["caseType"] {
  const map: Record<string, Case["caseType"]> = {
    MEDICAL_MALPRACTICE: "medical_malpractice",
    EMPLOYMENT_DISCRIMINATION: "employment_discrimination",
    COMMERCIAL_DISPUTE: "commercial_litigation",
    CONTRACT_BREACH: "other",
    OTHER: "other",
  };
  return map[backendType] || "other";
}

function mapDocTypeToBackend(frontendType: string): string {
  const map: Record<string, string> = {
    deposition: "PRIOR_DEPOSITION",
    medical_record: "MEDICAL_RECORDS",
    correspondence: "CORRESPONDENCE",
    exhibit: "EXHIBIT",
    other: "OTHER",
  };
  return map[frontendType] || "OTHER";
}

function mapDocStatusToFrontend(status: string): CaseDocument["status"] {
  const map: Record<string, CaseDocument["status"]> = {
    PENDING: "uploading",
    UPLOADING: "uploading",
    INDEXING: "indexing",
    READY: "ready",
    FAILED: "failed",
  };
  return map[status] || "uploading";
}

function mapCase(raw: Record<string, unknown>): Case {
  return {
    id: raw.id as string,
    name: (raw.caseName ?? raw.name) as string,
    caseType: mapCaseTypeToFrontend(raw.caseType as string),
    opposingFirm: (raw.opposingParty ?? raw.opposingFirm) as string | undefined,
    depositionDate: raw.depositionDate as string,
    witnessCount: (raw.witnessCount as number) ?? 0,
    documentCount: (raw.documentCount as number) ?? 0,
    sessionCount: (raw.sessionCount as number) ?? 0,
    status: "active",
    createdAt: raw.createdAt as string,
    updatedAt: (raw.updatedAt as string) ?? (raw.createdAt as string),
  };
}

function mapDocument(raw: Record<string, unknown>): CaseDocument {
  return {
    id: raw.id as string,
    caseId: raw.caseId as string ?? "",
    fileName: raw.filename as string,
    fileSize: raw.fileSizeBytes as number,
    mimeType: raw.mimeType as string,
    status: mapDocStatusToFrontend(raw.ingestionStatus as string),
    documentType: "other",
    pageCount: raw.pageCount as number | undefined,
    uploadedAt: raw.createdAt as string,
    error: raw.ingestionError as string | undefined,
  };
}
