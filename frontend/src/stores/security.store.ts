import { SecurityService } from "@/services/security-service";
import { ApiKeyBasic } from "@/types/security.types";
import { create } from "zustand";


interface SecurityState {
    isLoading: boolean;
    error: string | null;
    recentApiKeys: ApiKeyBasic[];
    
    // Actions
    changePassword: (userId: string, currentPassword: string, newPassword: string) => Promise<void>;
    fetchRecentApiKeys: () => Promise<void>;
    clearError: () => void;
}

export const useSecurityStore = create<SecurityState>()((set) => ({
    isLoading: false,
    error: null,
    recentApiKeys: [],

    changePassword: async (userId: string, currentPassword: string, newPassword: string) => {
        set({ isLoading: true, error: null });
        try {
            await SecurityService.changePassword(userId, {
                current_password: currentPassword,
                new_password: newPassword,
                confirm_new_password: newPassword
            });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to change password';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    fetchRecentApiKeys: async () => {
        set({ isLoading: true, error: null });
        try {
            const recentApiKeys = await SecurityService.getRecentApiKeys();
            set({ recentApiKeys });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch API keys';
            set({ error: errorMessage });
        } finally {
            set({ isLoading: false });
        }
    },

    clearError: () => set({ error: null }),
}));