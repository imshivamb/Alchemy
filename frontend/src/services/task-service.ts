import axiosInstance from "@/lib/axios/axios-instance";
import { WorkflowTask } from "@/types/workflow-api.types";
import axios, { AxiosResponse } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export class TaskService {
    static async getTasks(): Promise<WorkflowTask[]> {
        try {
            const response: AxiosResponse<WorkflowTask[]> = await axiosInstance.get(
                `${API_BASE_URL}/tasks/`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch tasks');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async createTask(data: Partial<WorkflowTask>): Promise<WorkflowTask> {
        try {
            const response: AxiosResponse<WorkflowTask> = await axiosInstance.post(
                `${API_BASE_URL}/tasks/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error creating task');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getTaskById(taskId: number): Promise<WorkflowTask> {
        try {
            const response: AxiosResponse<WorkflowTask> = await axiosInstance.get(
                `${API_BASE_URL}/tasks/${taskId}/`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching task');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async updateTask(taskId: number, data: Partial<WorkflowTask>): Promise<WorkflowTask> {
        try {
            const response: AxiosResponse<WorkflowTask> = await axiosInstance.patch(
                `${API_BASE_URL}/tasks/${taskId}/`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error updating task');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async deleteTask(taskId: number): Promise<void> {
        try {
            await axiosInstance.delete(
                `${API_BASE_URL}/tasks/${taskId}/`
            );
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error deleting task');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}