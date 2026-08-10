import { type FormEvent, useMemo, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  Bot,
  CheckCircle2,
  ChevronDown,
  FileUp,
  Files,
  Loader2,
  LogOut,
  Settings,
  UserCircle,
  Users,
} from "lucide-react";

import { UserManagementPanel } from "@/components/users/user-management";
import { DocumentListPanel } from "@/components/documents/document-list";
import { ChatBotSection } from "@/components/chat/chat-bot";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useDocumentOptions,
  useDocumentUpload,
} from "@/hooks/api";
import type { DocumentUploadResponse } from "@/api/types";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";

type ActiveSection = "system-config" | "chat-bot";
type SystemConfigView = "upload-document" | "documents" | "user-management";

const systemConfigItems: Array<{
  id: SystemConfigView;
  label: string;
  icon: typeof FileUp;
}> = [
  {
    id: "upload-document",
    label: "Upload Document",
    icon: FileUp,
  },
  {
    id: "documents",
    label: "Documents",
    icon: Files,
  },
  {
    id: "user-management",
    label: "User Management",
    icon: Users,
  },
];

export function HomePage() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const isAdmin = user?.role === "admin";
  const logout = useAuthStore((state) => state.logout);
  const [activeSection, setActiveSection] = useState<ActiveSection>(() =>
    isAdmin ? "system-config" : "chat-bot",
  );
  const [activeConfigView, setActiveConfigView] =
    useState<SystemConfigView>("upload-document");

  async function handleLogout() {
    logout();
    await navigate({ to: "/" });
  }

  return (
    <main className="min-h-screen bg-background">
      <nav className="border-b bg-white/85 backdrop-blur">
        <div className="mx-auto flex min-h-16 w-full max-w-7xl flex-wrap items-center justify-between gap-4 px-5 py-3 md:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
              SD
            </div>
            <div>
              <p className="text-sm font-semibold leading-5">SalesDesk</p>
              <p className="text-xs text-muted-foreground">Workspace</p>
            </div>
          </div>

          <div className="flex w-full items-center gap-2 sm:w-auto">
            {isAdmin ? (
              <SectionButton
                active={activeSection === "system-config"}
                icon={Settings}
                label="System Config"
                onClick={() => setActiveSection("system-config")}
              />
            ) : null}
            <SectionButton
              active={activeSection === "chat-bot"}
              icon={Bot}
              label="Chat Bot"
              onClick={() => setActiveSection("chat-bot")}
            />
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 text-sm sm:flex">
              <UserCircle className="h-5 w-5 text-muted-foreground" />
              <span className="max-w-40 truncate font-medium">
                {user?.name ?? user?.email ?? "User"}
              </span>
            </div>
            <Button variant="outline" size="sm" className="gap-2" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </nav>

      {activeSection === "system-config" && isAdmin ? (
        <SystemConfigSection
          activeView={activeConfigView}
          onViewChange={setActiveConfigView}
        />
      ) : (
        <ChatBotSection />
      )}
    </main>
  );
}

function SectionButton({
  active,
  icon: Icon,
  label,
  onClick,
}: {
  active: boolean;
  icon: typeof Settings;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex h-10 items-center gap-2 rounded-md border px-3 text-sm font-medium transition-colors",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border bg-white text-muted-foreground hover:bg-muted hover:text-foreground",
      )}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </button>
  );
}

function SystemConfigSection({
  activeView,
  onViewChange,
}: {
  activeView: SystemConfigView;
  onViewChange: (view: SystemConfigView) => void;
}) {
  return (
    <div className="mx-auto grid w-full max-w-7xl gap-6 px-5 py-6 md:grid-cols-[240px_1fr] md:px-8">
      <aside className="rounded-lg border bg-white">
        <div className="border-b px-4 py-3">
          <p className="text-sm font-semibold">System Config</p>
        </div>
        <div className="p-2">
          {systemConfigItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onViewChange(item.id)}
                className={cn(
                  "flex h-10 w-full items-center gap-2 rounded-md px-3 text-left text-sm font-medium transition-colors",
                  activeView === item.id
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </div>
      </aside>

      <section>
        {activeView === "upload-document" ? (
          <UploadDocumentPanel
            onUploadComplete={() => onViewChange("documents")}
          />
        ) : null}
        {activeView === "documents" ? <DocumentListPanel /> : null}
        {activeView === "user-management" ? <UserManagementPanel /> : null}
      </section>
    </div>
  );
}

function UploadDocumentPanel({
  onUploadComplete,
}: {
  onUploadComplete: () => void;
}) {
  const [documentName, setDocumentName] = useState("");
  const [category, setCategory] = useState("");
  const [productName, setProductName] = useState("");
  const [allowedRoles, setAllowedRoles] = useState<string[]>([]);
  const { accessRoles, documentCategories } = useDocumentOptions();
  const uploadAction = useDocumentUpload();
  const [file, setFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState("");
  const [uploadedDocument, setUploadedDocument] =
    useState<DocumentUploadResponse | null>(null);
  const isUploading = uploadAction.isLoading;
  const error = validationError || uploadAction.error;

  const canSubmit = useMemo(
    () =>
      documentName.trim().length > 0 &&
      category.trim().length > 0 &&
      allowedRoles.length > 0 &&
      !!file &&
      !isUploading,
    [allowedRoles, category, documentName, file, isUploading],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!file) {
      setValidationError("Select a document before uploading.");
      return;
    }

    setValidationError("");
    uploadAction.clearError();
    setUploadedDocument(null);

    const formData = new FormData();
    formData.append("document_name", documentName.trim());
    formData.append("category", category.trim());
    formData.append("allowed_roles", allowedRoles.join(","));
    formData.append("file", file);

    if (productName.trim()) {
      formData.append("product_name", productName.trim());
    }

    const uploaded = await uploadAction.execute(formData);

    if (uploaded) {
      setUploadedDocument(uploaded);
      setDocumentName("");
      setCategory("");
      setProductName("");
      setAllowedRoles([]);
      setFile(null);
      event.currentTarget.reset();
      onUploadComplete();
    }
  }

  return (
    <div className="rounded-lg border bg-white">
      <div className="border-b px-5 py-4">
        <div className="flex items-center gap-2">
          <FileUp className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">Upload Document</h1>
        </div>
      </div>

      <form className="grid gap-5 p-5 md:grid-cols-2" onSubmit={handleSubmit}>
        <Field label="Document Name" htmlFor="document_name" required>
          <Input
            id="document_name"
            value={documentName}
            onChange={(event) => setDocumentName(event.target.value)}
            placeholder="Quarterly furniture catalog"
          />
        </Field>

        <Field label="Category" htmlFor="category" required>
          <select
            id="category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="flex h-11 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="">Select a category</option>
            {documentCategories.map((documentCategory) => (
              <option key={documentCategory} value={documentCategory}>
                {formatRoleLabel(documentCategory)}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Product Name" htmlFor="product_name">
          <Input
            id="product_name"
            value={productName}
            onChange={(event) => setProductName(event.target.value)}
            placeholder="Optional product or collection"
          />
        </Field>

        <Field label="Who Has Access" htmlFor="allowed_roles" required>
          <RoleMultiSelect
            id="allowed_roles"
            options={accessRoles}
            selectedRoles={allowedRoles}
            onChange={setAllowedRoles}
          />
        </Field>

        <Field label="Document File" htmlFor="file" required className="md:col-span-2">
          <Input
            id="file"
            type="file"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </Field>

        {error ? (
          <div className="rounded-md border border-destructive/25 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive md:col-span-2">
            {error}
          </div>
        ) : null}

        {uploadedDocument ? (
          <div className="flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-800 md:col-span-2">
            <CheckCircle2 className="h-4 w-4" />
            Saved {uploadedDocument.original_filename} as{" "}
            {uploadedDocument.document_name}. A same-name file replaces the previous version.
          </div>
        ) : null}

        <div className="flex justify-end md:col-span-2">
          <Button type="submit" className="gap-2" disabled={!canSubmit}>
            {isUploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileUp className="h-4 w-4" />
            )}
            {isUploading ? "Uploading" : "Upload Document"}
          </Button>
        </div>
      </form>
    </div>
  );
}

function RoleMultiSelect({
  id,
  onChange,
  options,
  selectedRoles,
}: {
  id: string;
  onChange: (roles: string[]) => void;
  options: string[];
  selectedRoles: string[];
}) {
  const [isOpen, setIsOpen] = useState(false);
  const selectedLabels = options
    .filter((role) => selectedRoles.includes(role))
    .map(formatAccessRoleLabel);

  function toggleRole(role: string) {
    if (selectedRoles.includes(role)) {
      onChange(selectedRoles.filter((selectedRole) => selectedRole !== role));
      return;
    }

    onChange([...selectedRoles, role]);
  }

  return (
    <div className="relative">
      <button
        id={id}
        type="button"
        className="flex min-h-11 w-full items-center justify-between gap-3 rounded-md border bg-background px-3 py-2 text-left text-sm shadow-sm outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring"
        onClick={() => setIsOpen((current) => !current)}
      >
        <span
          className={cn(
            "min-w-0 flex-1 truncate",
            selectedLabels.length === 0 && "text-muted-foreground",
          )}
        >
          {selectedLabels.length > 0
            ? selectedLabels.join(", ")
            : "Select access roles"}
        </span>
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
            isOpen && "rotate-180",
          )}
        />
      </button>

      {isOpen ? (
        <div className="absolute z-20 mt-2 w-full rounded-md border bg-white p-2 shadow-lg">
          {options.map((role) => {
            const checked = selectedRoles.includes(role);

            return (
              <label
                key={role}
                className="flex cursor-pointer items-center gap-3 rounded-md px-2 py-2 text-sm font-medium hover:bg-muted"
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleRole(role)}
                  className="h-4 w-4 accent-primary"
                />
                <span>{formatAccessRoleLabel(role)}</span>
              </label>
            );
          })}
          <div className="mt-2 border-t pt-2">
            <Button
              type="button"
              size="sm"
              className="w-full"
              onClick={() => setIsOpen(false)}
            >
              OK
            </Button>
          </div>
        </div>
      ) : null}

      {selectedRoles.length > 0 ? (
        <div className="mt-2 flex flex-wrap gap-2">
          {selectedLabels.map((label) => (
            <span
              key={label}
              className="rounded-md border bg-muted px-2 py-1 text-xs font-medium text-foreground"
            >
              {label}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function formatRoleLabel(role: string) {
  return role
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatAccessRoleLabel(role: string) {
  if (role === "sales") {
    return "Salesperson";
  }

  return formatRoleLabel(role);
}

function Field({
  children,
  className,
  htmlFor,
  label,
  required = false,
}: {
  children: React.ReactNode;
  className?: string;
  htmlFor: string;
  label: string;
  required?: boolean;
}) {
  return (
    <div className={cn("space-y-2", className)}>
      <Label htmlFor={htmlFor}>
        {label}
        {required ? <span className="text-destructive"> *</span> : null}
      </Label>
      {children}
    </div>
  );
}
