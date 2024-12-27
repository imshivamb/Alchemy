import axiosInstance from "@/lib/axios/axios-instance";
import { User } from "@/types/auth.types";
import { UpdateProfileData, UpdateProfilePictureResponse } from "@/types/user.types";
import axios, { AxiosResponse } from "axios";

const API_BASE_URL =  process.env.NEXT_PUBLIC_API_BASE_URL || '';

export class UserService {
    static async updateProfilePicture(userId: string, file: File): Promise<UpdateProfilePictureResponse> {
        try {
            const formData = new FormData();
            formData.append('profile_picture', file);

            const response: AxiosResponse<UpdateProfilePictureResponse> = await axiosInstance.post(
                `${API_BASE_URL}/auth/users/${userId}/profile-picture/`,
                formData,
                {
                  headers: {
                    'Content-Type': 'multipart/form-data',
                  },
                }
              );
            return response.data
        } catch (error) {
            if (axios.isAxiosError(error)) {
                console.error('Response data:', error.response?.data);
                throw new Error(error.response?.data?.detail || 'Error uploading profile picture');
            }
            throw new Error('An unexpected error occurred while uploading profile picture');
        }
    }

    static async updateProfileData(userId: string, data: UpdateProfileData): Promise<User> {
        try {
            const response: AxiosResponse<User> = await axiosInstance.put(
                `${API_BASE_URL}/auth/users/${userId}/`,
                data,
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                console.error('Response data:', error.response?.data);
                throw new Error(error.response?.data?.detail || 'Error updating profile');
            }
            throw new Error('An unexpected error occurred while updating profile');
        }
    }
}