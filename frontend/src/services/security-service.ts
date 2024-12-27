import axiosInstance from "@/lib/axios/axios-instance";
import axios from "axios";
import { ApiKeyBasic, ChangePasswordData } from "@/types/security.types";


export class SecurityService {
    static async changePassword(userId: string, data: ChangePasswordData): Promise<void> {
        try {
            await axiosInstance.put(
                `/auth/users/${userId}/`,
                {
                    password: data.new_password,
                    current_password: data.current_password
                }
            );
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error changing password');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getRecentApiKeys(): Promise<ApiKeyBasic[]> {
        try {
            const response = await axiosInstance.get(`/auth/api-keys`);
            return response.data.slice(0, 3);
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching recent API keys');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}