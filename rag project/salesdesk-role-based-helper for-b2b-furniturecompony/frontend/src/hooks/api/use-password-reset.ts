import {
  confirmPasswordReset,
  requestPasswordReset,
  verifyPasswordReset,
} from "@/api/auth-api";
import { useApiAction } from "@/hooks/api/use-api-action";

export function usePasswordResetRequest() {
  return useApiAction(requestPasswordReset);
}

export function usePasswordResetVerification() {
  return useApiAction(verifyPasswordReset);
}

export function usePasswordResetConfirmation() {
  return useApiAction(confirmPasswordReset);
}
