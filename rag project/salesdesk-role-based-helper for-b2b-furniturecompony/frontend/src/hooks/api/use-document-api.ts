import { useCallback, useEffect, useState } from "react";

import { getAccessRoles } from "@/api/auth-api";
import {
  deleteDocument,
  getDocuments,
  getDocumentCategories,
  uploadDocument,
} from "@/api/document-api";
import type { ManagedDocument } from "@/api/types";
import { useApiAction } from "@/hooks/api/use-api-action";

const fallbackAccessRoles = ["admin", "sales", "manager"];
const fallbackDocumentCategories = ["product", "policy", "catalog", "pricing"];

export function useDocumentOptions() {
  const [accessRoles, setAccessRoles] = useState<string[]>(fallbackAccessRoles);
  const [documentCategories, setDocumentCategories] = useState<string[]>(
    fallbackDocumentCategories,
  );

  const loadOptions = useCallback(async () => {
    const [rolesResult, categoriesResult] = await Promise.allSettled([
      getAccessRoles(),
      getDocumentCategories(),
    ]);

    if (rolesResult.status === "fulfilled" && rolesResult.value.roles.length > 0) {
      setAccessRoles(rolesResult.value.roles);
    }

    if (
      categoriesResult.status === "fulfilled" &&
      categoriesResult.value.categories.length > 0
    ) {
      setDocumentCategories(categoriesResult.value.categories);
    }
  }, []);

  useEffect(() => {
    void loadOptions();
  }, [loadOptions]);

  return {
    accessRoles,
    documentCategories,
    refreshOptions: loadOptions,
  };
}

export function useDocumentUpload() {
  return useApiAction(uploadDocument);
}

export function useDocumentManagement() {
  const [documents, setDocuments] = useState<ManagedDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async (showLoading = true) => {
    if (showLoading) {
      setIsLoading(true);
    }
    setError("");

    try {
      setDocuments(await getDocuments());
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Unable to load documents.",
      );
    } finally {
      if (showLoading) {
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    const hasProcessingDocument = documents.some(
      (document) => document.status === "PROCESSING",
    );

    if (!hasProcessingDocument) {
      return;
    }

    const timer = window.setTimeout(() => {
      void refresh(false);
    }, 3000);

    return () => window.clearTimeout(timer);
  }, [documents, refresh]);

  async function removeDocument(documentId: number) {
    setError("");

    try {
      await deleteDocument(documentId);
      setDocuments((current) =>
        current.filter((document) => document.id !== documentId),
      );
      return true;
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : "Unable to delete document.",
      );
      return false;
    }
  }

  return {
    documents,
    isLoading,
    error,
    refresh: () => refresh(true),
    removeDocument,
  };
}
