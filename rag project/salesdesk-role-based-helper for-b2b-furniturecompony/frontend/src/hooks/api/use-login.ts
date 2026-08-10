import { login } from "@/api/auth-api";
import { useApiAction } from "@/hooks/api/use-api-action";

export function useLogin() {
  return useApiAction(login);
}
