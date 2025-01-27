import axiosInstance from "@/lib/axios/axios-instance";
import { AIConfig, AITask, AIModel, CostEstimate } from "@/types/ai.types";
import axios from "axios";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';

export class AIService {
   static async processAI(config: AIConfig): Promise<string> {
       try {
           const response = await axiosInstance.post(
               `${FASTAPI_BASE_URL}/ai/process`,
               config
           );
           return response.data.task_id;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error processing AI request');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async processBatch(configs: AIConfig[]): Promise<string[]> {
       try {
           const response = await axiosInstance.post(
               `${FASTAPI_BASE_URL}/ai/batch`,
               { configs }
           );
           return response.data.task_ids;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error processing batch requests');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getModels(): Promise<AIModel[]> {
       try {
           const response = await axiosInstance.get(
               `${FASTAPI_BASE_URL}/ai/models`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error fetching AI models');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async estimateCost(config: AIConfig): Promise<CostEstimate> {
       try {
           const response = await axiosInstance.post(
               `${FASTAPI_BASE_URL}/ai/estimate`,
               config
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error estimating cost');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getTaskStatus(taskId: string): Promise<AITask> {
       try {
           const response = await axiosInstance.get(
               `${FASTAPI_BASE_URL}/ai/status/${taskId}`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error fetching task status');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async listTasks(params?: {
       workflow_id?: string;
       status?: string;
       limit?: number;
       offset?: number;
   }): Promise<AITask[]> {
       try {
           const response = await axiosInstance.get(
               `${FASTAPI_BASE_URL}/ai/tasks`,
               { params }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error fetching tasks list');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async cancelTask(taskId: string): Promise<void> {
       try {
           await axiosInstance.post(
               `${FASTAPI_BASE_URL}/ai/tasks/${taskId}/cancel`
           );
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error cancelling task');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async retryTask(taskId: string): Promise<void> {
       try {
           await axiosInstance.post(
               `${FASTAPI_BASE_URL}/ai/tasks/${taskId}/retry`
           );
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Error retrying task');
           }
           throw new Error('An unexpected error occurred');
       }
   }
}