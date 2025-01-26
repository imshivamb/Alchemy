import axiosInstance from "@/lib/axios/axios-instance";
import { BaseWebhook, FastAPIWebhook, WebhookDelivery, WebhookHealth, WebhookStatus } from "@/types/webhook.types";
import axios, { AxiosResponse } from "axios";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';
const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';

export class WebhookService {
    // Django Basic CRUD Operations
    static async getWebhooks(): Promise<FastAPIWebhook[]> {
        try {
            // Get webhooks from both Django and FastAPI
            const djangoResponse: AxiosResponse<BaseWebhook[]> = await axiosInstance.get(
                `${API_BASE_URL}/webhooks/`
            );
            
            // Fetch additional data from FastAPI
            const fastAPIResponse: AxiosResponse<FastAPIWebhook[]> = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/webhooks`
            );
    
            // Merge the data
            return djangoResponse.data.map(djangoWebhook => {
                const fastAPIWebhook = fastAPIResponse.data.find(fw => fw.id === djangoWebhook.id);
                if (!fastAPIWebhook) {
                    // If no FastAPI data, create default FastAPI fields
                    return {
                        ...djangoWebhook,
                        status: WebhookStatus.PENDING,
                        total_deliveries: 0,
                        successful_deliveries: 0,
                        failed_deliveries: 0,
                        secret: {
                            key: '',
                            header_name: 'X-Webhook-Signature',
                            hash_algorithm: 'sha256'
                        }
                    } as FastAPIWebhook;
                }
                return fastAPIWebhook;
            });
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw error;
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async createWebhook(data: Partial<BaseWebhook>): Promise<FastAPIWebhook> {
        try {
            // First create in Django
            const response = await axiosInstance.post(`${API_BASE_URL}/webhooks/`, data);
    
            // Register with FastAPI using Django's trigger_url
            const fastAPIResponse = await axiosInstance.post(
                `${FASTAPI_BASE_URL}/webhooks`,
                {
                    name: data.name,
                    config: {
                        url: response.data.trigger_url,
                        method: "POST",
                        retry_strategy: {
                            max_retries: 3,
                            initial_interval: 60,
                            max_interval: 3600,
                            multiplier: 2
                        }
                    },
                    workflow_id: data.workflow?.toString(),
                    webhook_id: response.data.id
                }
            );
    
            return {
                ...response.data,
                ...fastAPIResponse.data
            };
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error creating webhook');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async updateWebhook(webhookId: string, data: Partial<BaseWebhook>): Promise<FastAPIWebhook> {
        try {
            // Update in Django
            await axiosInstance.patch(
                `${API_BASE_URL}/webhooks/${webhookId}/`,
                data
            );
    
            // Update in FastAPI
            const fastAPIResponse: AxiosResponse<FastAPIWebhook> = await axiosInstance.put(
                `${FASTAPI_BASE_URL}/webhooks/${webhookId}`,
                {
                    name: data.name,
                    config: data.config,
                    workflow_id: data.workflow?.toString()
                }
            );
    
            // Return FastAPI response as it has all fields
            return fastAPIResponse.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Error updating webhook');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async deleteWebhook(webhookId: string): Promise<void> {
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

    static async getWebhookDetails(webhookId: string): Promise<FastAPIWebhook> {
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

    static async triggerWebhook(webhookId: string, payload: any): Promise<string> {
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

    static async getDeliveries(webhookId: string, params?: {status?: string, limits?: number, offset?: number}): Promise<WebhookDelivery[]> {
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

    static async testWebhookProxy(data: {
        target_url: string;
        method?: string;
        headers?: Record<string, string>;
        payload?: any;
      }): Promise<{
        status: number;
        headers: Record<string, string>;
        body: string;
      }> {
        try {
          const response = await axiosInstance.post(
            `${FASTAPI_BASE_URL}/webhooks/test-proxy`,
            {
              method: data.method || 'POST',
              target_url: data.target_url,
              headers: data.headers || {},
              payload: data.payload
            }
          );
      
          // Convert Axios headers to plain string dictionary
          const headers: Record<string, string> = {};
          for (const [key, value] of Object.entries(response.headers)) {
            if (Array.isArray(value)) {
              headers[key] = value.join(', ');
            } else {
              headers[key] = String(value ?? '');
            }
          }
      
          return {
            status: response.status,
            headers,
            body: JSON.stringify(response.data)
          };
        } catch (error) {
          if (axios.isAxiosError(error)) {
            const message = error.response?.data?.detail || 
              error.message || 
              'Proxy request failed';
            const status = error.response?.status || 500;
            
            throw new Error(`${status}: ${message}`);
          }
          throw new Error('An unexpected error occurred during proxy request');
        }
      }
}