import { useAuthStore } from "@/store/auth-store";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type ApiRequestOptions = RequestInit & {
  authenticated?: boolean;
};

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { authenticated = false, headers: requestHeaders, ...requestInit } = options;
  const headers = new Headers(requestHeaders);

  if (authenticated) {
    const { accessToken, tokenType } = useAuthStore.getState();

    if (accessToken) {
      headers.set("Authorization", `${tokenType || "Bearer"} ${accessToken}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestInit,
    headers,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function jsonRequestBody(value: unknown) {
  return {
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(value),
  };
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function readErrorMessage(response: Response) {
  try {
    const data = (await response.json()) as {
      detail?: string | Array<{ msg?: string }>;
      message?: string;
      errors?: Array<{ message?: string }>;
    };

    if (typeof data.detail === "string") {
      return data.detail;
    }

    return (
      data.errors?.[0]?.message ??
      data.detail?.[0]?.msg ??
      data.message ??
      "The request could not be completed."
    );
  } catch {
    return "The server did not return a valid response.";
  }
}
