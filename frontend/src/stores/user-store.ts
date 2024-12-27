import { create } from "zustand";
import { UserService } from "@/services/user-service";
import { UpdateProfileData } from "@/types/user.types";
import { AuthStore } from "./auth.store";

interface UserState {
  isUpdating: boolean;
  error: string | null;
  profilePictureUrl: string | null;
  
  // Actions
  updateProfilePicture: (userId: string, file: File) => Promise<void>;
  updateProfile: (userId: string, data: UpdateProfileData) => Promise<void>;
  clearError: () => void;
}

export const useUserStore = create<UserState>()((set) => ({
  isUpdating: false,
  profilePictureUrl: null,
  error: null,

  updateProfilePicture: async (userId: string, file: File) => {
    set({ isUpdating: true });
    try {
      const response = await UserService.updateProfilePicture(userId, file);
      set({ profilePictureUrl: response.profile_picture_url });
    } catch (error) {
      throw error;
    } finally {
      set({ isUpdating: false });
    }
  },

  updateProfile: async (userId: string, data: UpdateProfileData) => {
    set({ isUpdating: true, error: null });
    try {
      const updatedUser = await UserService.updateProfileData(userId, data);
      AuthStore.setState(state => ({
        user: {
          ...state.user,
          ...updatedUser
        }
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update profile';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ isUpdating: false });
    }
  },

  clearError: () => set({ error: null }),
}));