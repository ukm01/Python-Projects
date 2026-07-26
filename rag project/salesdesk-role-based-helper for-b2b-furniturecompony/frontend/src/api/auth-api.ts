import { apiRequest, jsonRequestBody } from "@/api/client";
import type { AccessRolesResponse, LoginResponse } from "@/api/types";

export function login(email: string, password: string) {
  return apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    ...jsonRequestBody({ email, password }),
  });
}

export function requestPasswordReset(email: string) {
  return apiRequest<{ message: string }>("/auth/password-reset/request", {
    method: "POST",
    ...jsonRequestBody({ email }),
  });
}

export function verifyPasswordReset(email: string, otp: string) {
  return apiRequest<{ reset_token: string }>("/auth/password-reset/verify", {
    method: "POST",
    ...jsonRequestBody({ email, otp }),
  });
}

export function confirmPasswordReset(
  resetToken: string,
  password: string,
  confirmPassword: string,
) {
  return apiRequest<{ message: string }>("/auth/password-reset/confirm", {
    method: "POST",
    ...jsonRequestBody({
      reset_token: resetToken,
      password,
      confirm_password: confirmPassword,
    }),
  });
}

export function getAccessRoles() {
  return apiRequest<AccessRolesResponse>("/auth/roles", {
    authenticated: true,
  });
}
