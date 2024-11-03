import axiosInstance from "@/lib/axios/axios-instance";
import { AuthResponse,  EmailVerificationStatus,  LoginData, PasswordResetConfirmData, RegisterData, User } from "@/types/auth.types";
import axios, { AxiosResponse } from "axios";

const API_BASE_URL =  process.env.NEXT_PUBLIC_API_BASE_URL || '';

export class AuthService {
    static async register(data: RegisterData): Promise<User> {
        try {
            const response: AxiosResponse<User> = await axiosInstance.post(`${API_BASE_URL}/register`, data, {
                headers: {
                    "Content-Type": "application/json",
                }
            });
            return response.data;
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                // `error.response?.data` will be the server's response if available
                throw new Error(error.response?.data || 'Error registering user');
              }
              throw new Error('An unexpected error occurred');
        }
    }

    static async login(data: LoginData): Promise<AuthResponse> {
        try {
            const response: AxiosResponse = await axiosInstance.post(`${API_BASE_URL}/login`, data);

            const authResponse: AuthResponse = {
                tokens: {
                    access: response.data.access,
                    refresh: response.data.refresh
                },
                user: response.data.user
            };

            // Store tokens
            localStorage.setItem('accessToken', authResponse.tokens.access);
            localStorage.setItem('refreshToken', authResponse.tokens.refresh);
            
            return authResponse;
        } catch (error) {
            console.error('Full error:', error);
            if (axios.isAxiosError(error)) {
                console.error('Response data:', error.response?.data);
                throw new Error(error.response?.data?.detail || 'Error logging in user');
            }
            throw error;
        }
    }

    static async logout(refreshToken: string): Promise<void> {
        try {
            await axiosInstance.post(`${API_BASE_URL}/logout`, { refreshToken }, {
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem('refreshToken')}`
                }
            });

            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data || 'Error logging out');
              }
              throw new Error('An unexpected error occurred');
        }
    }

    static async getCurrentUser(): Promise<User> {
        try {
            const response: AxiosResponse<User> = await axiosInstance.get(`${API_BASE_URL}/me`, {
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem('accessToken')}`
                }
            })
            return response.data;
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
              throw new Error(error.response?.data || 'Failed to fetch user profile');
            }
            throw new Error('An unexpected error occurred');
          }
    }

    static async refreshToken(refreshToken: string): Promise<{access: string}> {
        try {
            const response: AxiosResponse<{access: string}> = await axiosInstance.post(`${API_BASE_URL}/refresh`, { refreshToken }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            return response.data
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
              throw new Error(error.response?.data || 'Failed to refresh token');
            }
            throw new Error('An unexpected error occurred');
          }
    }

    static async requestPasswordReset(email: string): Promise<void> {
        try {
             await axiosInstance.post(`${API_BASE_URL}/password/reset`, { email }, {
                headers: {
                    "Content-Type": "application/json",
                }
            });
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
              throw new Error(error.response?.data || 'Error requesting password reset');
            }
            throw new Error('An unexpected error occurred');
          }
    }

    static async resetPasswordConfirm(data: PasswordResetConfirmData): Promise<void> {
        try {
            await axiosInstance.post(`${API_BASE_URL}/password/reset/confirm`, data, {
                headers: {
                    "Content-Type": "application/json",
                }
            })
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error confirming password reset');
            }
            throw new Error('An unexpected error occurred');
        }

    }

    static async verifyEmail(token: string): Promise<void> {
        try {
            await axiosInstance.post(`${API_BASE_URL}/email/verify`, { token }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            })
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
              throw new Error(error.response?.data || 'Error verifying email');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async resendVerificationEmail(email: string): Promise<void> {
        try {
            await axiosInstance.put(`${API_BASE_URL}/email/verify`, { email }, {
                headers: {
                    "Content-Type": "application/json",
                }
            })
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error resending verification email');
            }
            throw new Error('An unexpected error occurred');
        }
    }
    static async checkEmailVerificationStatus(email: string): Promise<EmailVerificationStatus> {
        try {
            const response: AxiosResponse<EmailVerificationStatus> = 
                await axiosInstance.get(`${API_BASE_URL}/email/verify?email=${encodeURIComponent(email)}`);
            return response.data;
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error checking email verification status');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}