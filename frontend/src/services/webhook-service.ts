import axiosInstance from "@/lib/axios/axios-instance";
import { BaseWebhook, FastAPIWebhook, WebhookDelivery, WebhookHealth } from "@/types/webhook.types";
import axios, { AxiosResponse } from "axios";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';
const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';

export class WebhookService {
    // Django Basic CRUD Operations
    static async getWebhooks(): Promise<BaseWebhook[]> {
        try {
            const response: AxiosResponse<BaseWebhook[]> = await axiosInstance.get(`${API_BASE_URL}/webhooks/`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch webhooks');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async createWebhook(data: Partial<BaseWebhook>): Promise<BaseWebhook> {
        try {
            const response: AxiosResponse<BaseWebhook> = await axiosInstance.post(`${API_BASE_URL}/webhooks/`, data);

            // Register Webhook with FastAPI
            const fastAPIData = {
                name: data.name,
                config: data.config,
                workflow_id: data.workflow?.toString(),
            }

            await axiosInstance.post(
                `${FASTAPI_BASE_URL}/webhooks`,
                fastAPIData
            );

            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error creating webhook');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async updateWebhook(webhookId: number, data: Partial<BaseWebhook>): Promise<BaseWebhook> {
        try {
            const response: AxiosResponse<BaseWebhook> = await axiosInstance.patch(`${API_BASE_URL}/webhooks/${webhookId}/`, data);

            // Update Webhook with FastAPI
            if(data.config) {
                await axiosInstance.put(
                    `${FASTAPI_BASE_URL}/webhooks/${webhookId}`,
                    { config: data.config }
                )
            }

            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error updating webhook');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async deleteWebhook(webhookId: number): Promise<void> {
        try {
            // Delete from both systems
            await Promise.all([
                axiosInstance.delete(`${API_BASE_URL}/webhooks/${webhookId}/`),
                axiosInstance.delete(`${FASTAPI_BASE_URL}/webhooks/${webhookId}`)
            ]);
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error deleting webhook');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    // FastAPI Specific Operations

    static async getWebhookDetails(webhookId: number): Promise<FastAPIWebhook> {
        try {
            const response: AxiosResponse<FastAPIWebhook> = await axiosInstance.get(`${FASTAPI_BASE_URL}/webhooks/${webhookId}/`);
            return response.data
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch webhook details');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async triggerWebhook(webhookId: number, payload: any): Promise<string> {
        try {
            const response: AxiosResponse<{delivery_id: string}> = await axiosInstance.post(`${FASTAPI_BASE_URL}/webhooks/${webhookId}/trigger`, payload);
            return response.data.delivery_id
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error triggering webhook');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getDeliveries(webhookId: number, params?: {status?: string, limits?: number, offset?: number}): Promise<WebhookDelivery[]> {
        try {
            const response: AxiosResponse<WebhookDelivery[]> = await axiosInstance.get(`${FASTAPI_BASE_URL}/webhooks/${webhookId}/deliveries`, {params});
            return response.data
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching deliveries');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getDeliveryDetails(deliveryId: string): Promise<WebhookDelivery> {
        try {
            const response: AxiosResponse<WebhookDelivery> = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/deliveries/${deliveryId}`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching delivery details');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async retryDelivery(deliveryId: string): Promise<void> {
        try {
            await axiosInstance.post(
                `${FASTAPI_BASE_URL}/deliveries/${deliveryId}/retry`
            );
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error retrying delivery');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async verifySignature(webhookId: string, payload: string, signature: string): Promise<boolean> {
        try {
            const response: AxiosResponse<{ valid: boolean }> = await axiosInstance.post(
                `${FASTAPI_BASE_URL}/webhooks/${webhookId}/verify`,
                { payload, signature }
            );
            return response.data.valid;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error verifying signature');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getWebhookHealth(webhookId: string): Promise<WebhookHealth> {
        try {
            const response: AxiosResponse<WebhookHealth> = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/webhooks/${webhookId}/health`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error fetching webhook health');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}