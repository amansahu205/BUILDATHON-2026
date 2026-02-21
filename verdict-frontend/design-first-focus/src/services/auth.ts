import { tokenStore } from "./api";
import { MOCK_USER, MOCK_TOKENS, MOCK_LOGIN_RESPONSE } from "@/mocks/data";
import type { LoginRequest, LoginResponse, User, FirmOnboardingPayload } from "@/types";

// Auto-seed tokens so the user is always "logged in"
if (!tokenStore.get()) {
  tokenStore.set(MOCK_TOKENS);
}

export const authService = {
  login: async (_payload: LoginRequest): Promise<LoginResponse> => {
    tokenStore.set(MOCK_TOKENS);
    return MOCK_LOGIN_RESPONSE;
  },

  ssoLogin: async (_provider: string): Promise<{ redirectUrl: string }> => {
    tokenStore.set(MOCK_TOKENS);
    return { redirectUrl: "/dashboard" };
  },

  logout: async (): Promise<void> => {
    tokenStore.clear();
  },

  me: async (): Promise<User> => {
    return MOCK_USER;
  },

  forgotPassword: async (_email: string): Promise<void> => {},

  resetPassword: async (_token: string, _password: string): Promise<void> => {},

  validateOnboardingToken: async (_token: string): Promise<{ firmName: string; adminEmail: string }> => {
    return { firmName: "Morrison & Associates", adminEmail: "sarah.chen@morrison-associates.com" };
  },

  completeOnboarding: async (_token: string, _payload: FirmOnboardingPayload): Promise<LoginResponse> => {
    tokenStore.set(MOCK_TOKENS);
    return MOCK_LOGIN_RESPONSE;
  },
};
