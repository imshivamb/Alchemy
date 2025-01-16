import axiosInstance from "@/lib/axios/axios-instance";
import { UpdateWorkspaceData, Workspace, WorkspaceMember, WorkspaceStats } from "@/types/workspace.types";
import axios, { AxiosResponse } from "axios";

const API_BASE_URL =  process.env.NEXT_PUBLIC_API_BASE_URL || '';

export class WorkspaceService {
    static async getWorkspaces(): Promise<Workspace[]> {
        try {
            const response: AxiosResponse<Workspace[]> = await axiosInstance.get(`${API_BASE_URL}/auth/workspaces`, {
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem('accessToken')}`
                }
            });
            return response.data;
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
              throw new Error(error.response?.data || 'Failed to fetch user workspaces');
            }
            throw new Error('An unexpected error occurred');
          }
    }

    static async getWorkspaceById(workspaceId: string): Promise<Workspace> {
        try {
            const response: AxiosResponse<Workspace> = await axiosInstance.get(
                `${API_BASE_URL}/auth/workspaces/${workspaceId}/`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching workspace');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async updateWorkspace(workspaceId: string, data: UpdateWorkspaceData): Promise<Workspace> {
        try {
            const response: AxiosResponse<Workspace> = await axiosInstance.patch(
                `${API_BASE_URL}/auth/workspaces/${workspaceId}/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error updating workspace');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getWorkspaceStats(workspaceId: string): Promise<WorkspaceStats> {
        try {
            const response: AxiosResponse<WorkspaceStats> = await axiosInstance.get(
                `${API_BASE_URL}/auth/workspaces/${workspaceId}/stats/`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching workspace stats');
            }
            throw new Error('An unexpected error occurred');
        }
    }
    static async createWorkspace(data: { name: string }): Promise<Workspace> {
        try {
            const response: AxiosResponse<Workspace> = await axiosInstance.post(
                `${API_BASE_URL}/auth/workspaces/`,
                data,
                {
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error creating workspace');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async deleteWorkspace(workspaceId: string): Promise<void> {
        try {
            await axiosInstance.delete(
                `${API_BASE_URL}/auth/workspaces/${workspaceId}/`
            );
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error deleting workspace');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async addWorkspaceMember(
        workspaceId: string, 
        data: { 
            email: string; 
            role: 'admin' | 'member';
        }
    ): Promise<WorkspaceMember> {
        try {
            const response: AxiosResponse<WorkspaceMember> = await axiosInstance.post(
                `${API_BASE_URL}/auth/workspaces/${workspaceId}/add_member/`,
                data,
                {
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error adding workspace member');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}