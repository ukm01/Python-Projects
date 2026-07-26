import { useAuthStore, type AuthUser } from "@/store/auth-store";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
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

export type AccessRolesResponse = {
  roles: string[];
};

export async function loginRequest(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    let message = "Unable to sign in with those credentials.";

    try {
      const data = (await response.json()) as { detail?: string; message?: string };
      message = data.detail ?? data.message ?? message;
    } catch {
      message = "The server did not return a valid login response.";
    }

    throw new Error(message);
  }

  return (await response.json()) as LoginResponse;
}

export function authHeaders(): Record<string, string> {
  const { accessToken, tokenType } = useAuthStore.getState();

  if (!accessToken) {
    return {};
  }

  return {
    Authorization: `${tokenType || "Bearer"} ${accessToken}`,
  };
}

export async function uploadDocumentRequest(formData: FormData) {
  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  if (!response.ok) {
    let message = "Unable to upload document.";

    try {
      const data = (await response.json()) as { detail?: string; message?: string };
      message = data.detail ?? data.message ?? message;
    } catch {
      message = "The server did not return a valid upload response.";
    }

    throw new Error(message);
  }

  return (await response.json()) as DocumentUploadResponse;
}

export async function getAccessRolesRequest() {
  const response = await fetch(`${API_BASE_URL}/auth/roles`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Unable to load access roles.");
  }

  return (await response.json()) as AccessRolesResponse;
}
