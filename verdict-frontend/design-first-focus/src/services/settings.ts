import { MOCK_SETTINGS, MOCK_ACTIVE_SESSIONS } from "@/mocks/data";
import type { AttorneySettings, ActiveSession } from "@/types";

export const settingsService = {
  get: async (): Promise<AttorneySettings> => {
    return MOCK_SETTINGS;
  },

  updateProfile: async (_payload: Partial<AttorneySettings["profile"]>): Promise<void> => {},

  updateSessionDefaults: async (_payload: Partial<AttorneySettings["sessionDefaults"]>): Promise<void> => {},

  updateNotifications: async (_payload: Partial<AttorneySettings["notifications"]>): Promise<void> => {},

  changePassword: async (_currentPassword: string, _newPassword: string): Promise<void> => {},

  getActiveSessions: async (): Promise<ActiveSession[]> => {
    return MOCK_ACTIVE_SESSIONS;
  },

  revokeSession: async (_sessionId: string): Promise<void> => {},
};
