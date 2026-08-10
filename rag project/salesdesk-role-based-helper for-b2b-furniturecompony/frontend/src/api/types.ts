import type { AuthUser } from "@/store/auth-store";

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type ManagedUser = {
  id: number;
  name: string;
  email: string;
  role: string;
  department: string | null;
  is_active: boolean;
  created_at: string;
};

export type CreateUserPayload = {
  name: string;
  email: string;
  password: string;
  role: string;
  department?: string;
};

export type UpdateUserPayload = {
  role?: string;
  department?: string | null;
  is_active?: boolean;
};

export type DocumentUploadResponse = {
  id: number;
  document_name: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  status: string;
  created_at: string;
};

export type ManagedDocument = {
  id: number;
  document_name: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  category: string;
  product_name: string | null;
  allowed_roles: string;
  uploaded_by: string;
  status: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export type AccessRolesResponse = {
  roles: string[];
};

export type DocumentCategoriesResponse = {
  categories: string[];
};

export type ChatCitation = {
  source_id: string;
  chunk_id: string;
  document_id: number;
  document_name: string;
  original_filename: string;
  page_number: number | null;
};

export type ChatResponse = {
  status: "answered" | "insufficient_context";
  answer: string;
  citations: ChatCitation[];
  model: string;
};
