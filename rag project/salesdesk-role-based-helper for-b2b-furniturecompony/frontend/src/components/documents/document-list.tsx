import { FileText, RefreshCw, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useDocumentManagement } from "@/hooks/api";

export function DocumentListPanel() {
  const {
    documents,
    isLoading,
    error,
    refresh,
    removeDocument,
  } = useDocumentManagement();

  async function handleDelete(documentId: number, filename: string) {
    const confirmed = window.confirm(
      `Delete ${filename}? The stored file and its vector data will be permanently removed.`,
    );

    if (confirmed) {
      await removeDocument(documentId);
    }
  }

  return (
    <div className="rounded-lg border bg-white">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          <div>
            <h1 className="text-lg font-semibold">Documents</h1>
            <p className="text-sm text-muted-foreground">
              Review uploaded files and remove obsolete content.
            </p>
          </div>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="gap-2"
          onClick={() => void refresh()}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {error ? (
        <div className="mx-5 mt-5 rounded-md border border-destructive/25 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive">
          {error}
        </div>
      ) : null}

      <div className="overflow-x-auto p-5">
        {isLoading ? (
          <div className="py-12 text-center text-sm text-muted-foreground">
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="py-12 text-center text-sm text-muted-foreground">
            No documents have been uploaded.
          </div>
        ) : (
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead>
              <tr className="border-b text-xs uppercase tracking-wide text-muted-foreground">
                <th className="px-3 py-3 font-semibold">Document</th>
                <th className="px-3 py-3 font-semibold">Category</th>
                <th className="px-3 py-3 font-semibold">Access</th>
                <th className="px-3 py-3 font-semibold">Status</th>
                <th className="px-3 py-3 font-semibold">Updated</th>
                <th className="px-3 py-3 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((document) => (
                <tr className="border-b last:border-0" key={document.id}>
                  <td className="px-3 py-4">
                    <p className="font-semibold">{document.document_name}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {document.original_filename} · {formatBytes(document.size_bytes)}
                    </p>
                  </td>
                  <td className="px-3 py-4">
                    <p>{formatLabel(document.category)}</p>
                    {document.product_name ? (
                      <p className="mt-1 text-xs text-muted-foreground">
                        {document.product_name}
                      </p>
                    ) : null}
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex flex-wrap gap-1">
                      {document.allowed_roles.split(",").filter(Boolean).map((role) => (
                        <span
                          className="rounded bg-muted px-2 py-1 text-xs font-medium"
                          key={role}
                        >
                          {formatRole(role)}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-3 py-4">
                    <StatusBadge status={document.status} />
                    {document.error_message ? (
                      <p
                        className="mt-1 max-w-52 truncate text-xs text-destructive"
                        title={document.error_message}
                      >
                        {document.error_message}
                      </p>
                    ) : null}
                  </td>
                  <td className="px-3 py-4 text-muted-foreground">
                    {new Date(document.updated_at).toLocaleDateString()}
                  </td>
                  <td className="px-3 py-4 text-right">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="gap-2 text-destructive hover:text-destructive"
                      disabled={document.status === "PROCESSING"}
                      onClick={() =>
                        void handleDelete(document.id, document.original_filename)
                      }
                      title={
                        document.status === "PROCESSING"
                          ? "Wait for processing to finish before deleting"
                          : undefined
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isReady = status === "READY";
  const isFailed = status === "FAILED";

  return (
    <span
      className={
        isReady
          ? "rounded bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-800"
          : isFailed
            ? "rounded bg-red-100 px-2 py-1 text-xs font-semibold text-red-800"
            : "rounded bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800"
      }
    >
      {formatLabel(status)}
    </span>
  );
}

function formatRole(role: string) {
  return role.trim() === "sales" ? "Salesperson" : formatLabel(role);
}

function formatLabel(value: string) {
  return value
    .trim()
    .toLowerCase()
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
