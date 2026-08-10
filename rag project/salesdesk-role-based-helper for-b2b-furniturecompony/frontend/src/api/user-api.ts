import { apiRequest, jsonRequestBody } from "@/api/client";
import type {
  CreateUserPayload,
  ManagedUser,
  UpdateUserPayload,
} from "@/api/types";

export function getUsers() {
  return apiRequest<ManagedUser[]>("/users", {
    authenticated: true,
  });
}

export function createUser(payload: CreateUserPayload) {
  return apiRequest<ManagedUser>("/users", {
    method: "POST",
    authenticated: true,
    ...jsonRequestBody(payload),
  });
}

export function updateUser(userId: number, payload: UpdateUserPayload) {
  return apiRequest<ManagedUser>(`/users/${userId}`, {
    method: "PATCH",
    authenticated: true,
    ...jsonRequestBody(payload),
  });
}

export function deleteUser(userId: number) {
  return apiRequest<void>(`/users/${userId}`, {
    method: "DELETE",
    authenticated: true,
  });
}
