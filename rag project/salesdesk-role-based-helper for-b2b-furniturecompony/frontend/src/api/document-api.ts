import { apiRequest } from "@/api/client";
import type {
  DocumentCategoriesResponse,
  DocumentUploadResponse,
  ManagedDocument,
} from "@/api/types";

export function uploadDocument(formData: FormData) {
  return apiRequest<DocumentUploadResponse>("/documents/upload", {
    method: "POST",
    authenticated: true,
    body: formData,
  });
}

export function getDocumentCategories() {
  return apiRequest<DocumentCategoriesResponse>("/documents/categories", {
    authenticated: true,
  });
}

export function getDocuments() {
  return apiRequest<ManagedDocument[]>("/documents", {
    authenticated: true,
  });
}

export function deleteDocument(documentId: number) {
  return apiRequest<void>(`/documents/${documentId}`, {
    method: "DELETE",
    authenticated: true,
  });
}
