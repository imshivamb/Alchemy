import { AuthService } from "@/services/auth-service";
import { LoginData, PasswordResetConfirmData, RegisterData, User } from "@/types/auth.types";
import {create} from "zustand";
import { persist } from "zustand/middleware";
import { jwtDecode } from "jwt-decode";


interface AuthState {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    isInitialized: boolean;
    
    // Core auth methods
    login: (data: LoginData) => Promise<void>;
    logout: () => Promise<void>;
    register: (data: RegisterData) => Promise<User>;
    
    // Profile and session management
    refreshUserProfile: () => Promise<void>;
    initAuth: () => Promise<void>;
    
    // Token and route protection
    checkAuth: () => boolean;
    isTokenValid: () => boolean;
    handleUnauthorized: () => void;

    // Password Reset
    requestPasswordReset: (email: string) => Promise<void>;
    resetPasswordConfirm: (data: PasswordResetConfirmData) => Promise<void>;

    // Email verification
    verifyEmail: (token: string) => Promise<void>;
    resendVerificationEmail: (email: string) => Promise<void>;
    checkEmailVerificationStatus: (email: string) => Promise<boolean>;
}

export const AuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        isInitialized: false,

            initAuth: async () => {
                const accessToken = localStorage.getItem('accessToken');
                if(!accessToken) {
                    set({ isInitialized: true });
                    return;
                }

                try {
                    if(!get().isTokenValid()) {
                        throw new Error('Invalid token');
                    }

                    const userProfile = await AuthService.getCurrentUser();
                    set({
                        user: userProfile,
                        isAuthenticated: true,
                        isInitialized: true
                    })
                } catch  {
                    get().handleUnauthorized();
                }
            },

            login: async (data) => {
                set({ isLoading: true });
                try {
                    const response = await AuthService.login(data);
                    set({ 
                        user: response.user, 
                        isAuthenticated: true 
                    });
                } catch (error) {
                    console.error('Login failed:', error);
                    throw error;
                } finally {
                    set({ isLoading: false });
                }
            },

            logout: async () => {
                set({ isLoading: true });
                try {
                    const refreshToken = localStorage.getItem('refreshToken');
                    if(refreshToken) {
                        await AuthService.logout(refreshToken);
                    }
                    get().handleUnauthorized();
                } catch (error) {
                    console.error('Logout error:', error);
                    get().handleUnauthorized();
                } finally {
                set({ isLoading: false });
                }
            },
    
            register: async (data) => {
                set({ isLoading: true });
                try {
                    const response = await AuthService.register(data);
                    return response;
                } catch (error) {
                    console.error('Registration failed:', error);
                    throw error;
                } finally {
                    set({ isLoading: false });
                }
            },

            refreshUserProfile: async () => {
                try {
                    if (!get().checkAuth()) {
                        return;
                    }
                    const userProfile = await AuthService.getCurrentUser();
                    set({ user: userProfile });
                } catch (error) {
                    console.error('Failed to refresh user profile:', error);
                    get().handleUnauthorized();
                }
            },

            checkAuth: () => {
                const state = get();
                return state.isAuthenticated && state.isTokenValid();
            },

            isTokenValid: () => {
                try {
                    const token = localStorage.getItem('accessToken');
                    if (!token) return false;

                    const decoded = jwtDecode(token);
                    if (!decoded.exp) return false;
                     // Adding 10-second buffer for clock skew
                     return decoded.exp > (Date.now() / 1000) - 10;
                } catch {
                    return false;
                }
            },

            handleUnauthorized: () => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('refreshToken');
                set({
                    user: null,
                    isAuthenticated: false
                })

                // Only redirect if we're in a browser environment
                if (typeof window !== 'undefined') {
                    window.location.href = '/login';
                }
            },

            requestPasswordReset: async (email: string) => {
                set({ isLoading: true });
                try {
                    await AuthService.requestPasswordReset(email);
                } catch (error) {
                    console.error('Password reset request failed:', error);
                    throw error;
                } finally {
                    set({ isLoading: false });
                }
            },

            resetPasswordConfirm: async(data: PasswordResetConfirmData) => {
                set({ isLoading: true });
                try {
                    await AuthService.resetPasswordConfirm(data);
                
                } catch (error) {
                    console.error('Password reset confirmation failed:', error);
                    throw error;
                } finally {
                    set({ isLoading: false });
                }
            },

            verifyEmail: async (token: string) => {
                set({ isLoading: true });
                try {
                    await AuthService.verifyEmail(token);
                    await get().refreshUserProfile();
                } catch (error) {
                    console.error('Email verification failed:', error);
                    throw error;
                } finally {
                    set({ isLoading: false });
                }
            },

            resendVerificationEmail: async (email: string) => {
                set({ isLoading: true });
                try {
                    await AuthService.resendVerificationEmail(email);
                } catch (error) {
                    console.error('Failed to resend verification email:', error);
                    throw error;
                } finally {
                    set({ isLoading: false });
                }
            },

            checkEmailVerificationStatus: async (email: string) => {
                try {
                    const response = await AuthService.checkEmailVerificationStatus(email);
                    return response.is_verified;
                } catch (error) {
                    console.error('Failed to check email verification status:', error);
                    throw error;
                }
            }
            }),
            {
                name: 'auth-storage',
                // Only persist necessary authentication state
                partialize: (state) => ({
                    isInitialized: state.isInitialized,
                    isAuthenticated: state.isAuthenticated,
                }),
            }

)
)