import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

export type AuthUser = {
  id: number;
  name: string;
  email: string;
  role: string;
  department: string | null;
  is_active: boolean;
};

type AuthState = {
  accessToken: string | null;
  tokenType: string;
  user: AuthUser | null;
  isAuthenticated: boolean;
  setSession: (session: {
    accessToken: string;
    tokenType: string;
    user: AuthUser;
  }) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      tokenType: "Bearer",
      user: null,
      isAuthenticated: false,
      setSession: ({ accessToken, tokenType, user }) =>
        set({
          accessToken,
          tokenType: normalizeTokenType(tokenType),
          user,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          accessToken: null,
          tokenType: "Bearer",
          user: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: "salesdesk-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        tokenType: state.tokenType,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);

function normalizeTokenType(tokenType: string) {
  return tokenType ? tokenType.charAt(0).toUpperCase() + tokenType.slice(1) : "Bearer";
}
