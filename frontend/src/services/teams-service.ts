// src/services/team-service.ts
import axios, { AxiosResponse } from 'axios';
import axiosInstance from "@/lib/axios/axios-instance";
import { CreateTeamData, TeamDetail, TeamMember } from '@/types/teams.types';


const API_BASE_URL =  process.env.NEXT_PUBLIC_API_BASE_URL || '';


export class TeamService {
    static async getTeams(workspaceId: string): Promise<TeamDetail[]> {
        try {
            const response: AxiosResponse<TeamDetail[]> = await axiosInstance.get(
                `${API_BASE_URL}/teams/`, {
                    params: { workspace: workspaceId }
                }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching teams');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getTeamById(teamId: string): Promise<TeamDetail> {
        try {
            const response: AxiosResponse<TeamDetail> = await axiosInstance.get(
                `${API_BASE_URL}/teams/${teamId}/`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching team');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async createTeam(data: CreateTeamData): Promise<TeamDetail> {
        try {
            const response: AxiosResponse<TeamDetail> = await axiosInstance.post(
                `${API_BASE_URL}/teams/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error creating team');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async updateTeam(teamId: string, data: Partial<CreateTeamData>): Promise<TeamDetail> {
        try {
            const response: AxiosResponse<TeamDetail> = await axiosInstance.patch(
                `${API_BASE_URL}/teams/${teamId}/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error updating team');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async deleteTeam(teamId: string): Promise<void> {
        try {
            await axiosInstance.delete(`${API_BASE_URL}/teams/${teamId}/`);
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error deleting team');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async addTeamMember(teamId: string, data: { user_id: string; role: string }): Promise<TeamMember> {
        try {
            const response: AxiosResponse<TeamMember> = await axiosInstance.post(
                `${API_BASE_URL}/teams/${teamId}/add_member/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error adding team member');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}