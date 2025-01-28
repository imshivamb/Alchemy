import axiosInstance from "@/lib/axios/axios-instance";
import { Workflow, CreateWorkflowData, WorkflowLimits } from "@/types/workflow-api.types";
import axios, { AxiosResponse } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export class WorkflowService {
    static async getWorkflows(): Promise<Workflow[]> {
        try {
            const response: AxiosResponse<{ results: Workflow[] }> = await axiosInstance.get(`${API_BASE_URL}/workflows/`);
            return response.data.results;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch workflows');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getWorkflowById(workflowId: number): Promise<Workflow> {
        try {
            const response: AxiosResponse<Workflow> = await axiosInstance.get(`${API_BASE_URL}/workflows/${workflowId}/`);
            return response.data
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching workflow');
            }
            throw new Error('An unexpected error occurred');
        }
    }
    static async createWorkflow(data: CreateWorkflowData): Promise<Workflow> {
        try {
            const response: AxiosResponse<Workflow> = await axiosInstance.post(
                `${API_BASE_URL}/workflows/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw error;
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async updateWorkflow(workflowId: number, data: Partial<CreateWorkflowData>): Promise<Workflow> {
        try {
            const response: AxiosResponse<Workflow> = await axiosInstance.patch(
                `${API_BASE_URL}/workflows/${workflowId}/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error updating workflow');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async deleteWorkflow(workflowId: number): Promise<void> {
        try {
            await axiosInstance.delete(
                `${API_BASE_URL}/workflows/${workflowId}/`
            );
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error deleting workflow');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getWorkflowLimits(): Promise<WorkflowLimits> {
        try {
            const response: AxiosResponse<WorkflowLimits> = await axiosInstance.get(
                `${API_BASE_URL}/workflows/limits/`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching workflow limits');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}