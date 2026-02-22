import { api, tokenStore } from "./api";
import type { LoginRequest, LoginResponse, User } from "@/types";

export const authService = {
  login: async (payload: LoginRequest): Promise<LoginResponse> => {
    const { data: resp } = await api.post("/auth/login", payload);
    const payloadData = resp?.data ?? resp;
    const { user, tokens } = payloadData;
    if (!tokens?.accessToken) throw new Error("Invalid login response");
    tokenStore.set(tokens);
    return { user, tokens };
  },

  ssoLogin: async (_provider: string): Promise<{ redirectUrl: string }> => {
    return { redirectUrl: "/dashboard" };
  },

  logout: async (): Promise<void> => {
    try {
      await api.post("/auth/logout");
    } catch {
      // ignore — still clear local tokens
    }
    tokenStore.clear();
  },

  me: async (): Promise<User> => {
    const { data: resp } = await api.get("/auth/me");
    return (resp?.data ?? resp) as User;
  },

  forgotPassword: async (_email: string): Promise<void> => {},
  resetPassword: async (_token: string, _password: string): Promise<void> => {},

  validateOnboardingToken: async (_token: string): Promise<{ firmName: string; adminEmail: string }> => {
    return { firmName: "Morrison & Associates", adminEmail: "admin@example.com" };
  },

  completeOnboarding: async (_token: string, _payload: unknown): Promise<LoginResponse> => {
    throw new Error("Not implemented");
  },
};
