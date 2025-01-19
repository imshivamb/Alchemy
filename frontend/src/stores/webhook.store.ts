import { create } from 'zustand';
import { WebhookService } from '@/services/webhook-service';
import { 
    BaseWebhook, 
    FastAPIWebhook, 
    WebhookDelivery, 
    WebhookHealth 
} from '@/types/webhook.types';

interface WebhookState {
    // State
    webhooks: BaseWebhook[];
    currentWebhook: FastAPIWebhook | null;
    deliveries: WebhookDelivery[];
    webhookHealth: WebhookHealth | null;
    isLoading: boolean;
    error: string | null;

    // Basic actions
    setCurrentWebhook: (webhook: FastAPIWebhook) => void;
    clearError: () => void;

    // Django CRUD actions
    fetchWebhooks: () => Promise<void>;
    createWebhook: (data: Partial<BaseWebhook>) => Promise<void>;
    updateWebhook: (webhookId: string, data: Partial<BaseWebhook>) => Promise<void>;
    deleteWebhook: (webhookId: string) => Promise<void>;

    // FastAPI advanced actions
    getWebhookDetails: (webhookId: string) => Promise<void>;
    triggerWebhook: (webhookId: string, payload: any) => Promise<string>;
    getDeliveries: (webhookId: string, params?: { 
        status?: string; 
        limit?: number; 
        offset?: number 
    }) => Promise<void>;
    getDeliveryDetails: (deliveryId: string) => Promise<WebhookDelivery>;
    retryDelivery: (deliveryId: string) => Promise<void>;
    verifySignature: (webhookId: string, payload: string, signature: string) => Promise<boolean>;
    getWebhookHealth: (webhookId: string) => Promise<void>;
}

export const useWebhookStore = create<WebhookState>((set) => ({
    
    // Initial state
    webhooks: [],
    currentWebhook: null,
    deliveries: [],
    webhookHealth: null,
    isLoading: false,
    error: null,

    // Basic actions
    setCurrentWebhook: (webhook) => set({ currentWebhook: webhook }),
    clearError: () => set({ error: null }),

    // Django CRUD actions
    fetchWebhooks: async () => {
        set({ isLoading: true, error: null });
        try {
            const webhooks = await WebhookService.getWebhooks();
            set({ webhooks });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch webhooks';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    createWebhook: async (data) => {
        set({ isLoading: false, error: null });
        try {
            const newWebhook = await WebhookService.createWebhook(data);

            set(state => ({
                webhooks: [...state.webhooks, newWebhook]
            }))
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to create webhook';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    updateWebhook: async (webhookId, data) => {
        set({ isLoading: true, error: null });
        try {
            const updatedWebhook = await WebhookService.updateWebhook(webhookId, data);
            set(state => ({
                webhooks: state.webhooks.map(w => 
                    w.id === webhookId ? updatedWebhook : w
                ),
                currentWebhook: state.currentWebhook?.id === webhookId 
                    ? { ...state.currentWebhook, ...updatedWebhook }
                    : state.currentWebhook
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to update webhook';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    deleteWebhook: async (webhookId) => {
        set({ isLoading: true, error: null });
        try {
            await WebhookService.deleteWebhook(webhookId);
            set(state => ({
                webhooks: state.webhooks.filter(w => w.id !== webhookId),
                currentWebhook: state.currentWebhook?.id === webhookId 
                    ? null 
                    : state.currentWebhook
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to delete webhook';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    // FastAPI advanced actions
    getWebhookDetails: async (webhookId) => {
        set({ isLoading: true, error: null });
        try {
            const webhook = await WebhookService.getWebhookDetails(webhookId);
            set({ currentWebhook: webhook });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch webhook details';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    triggerWebhook: async (webhookId, payload) => {
        set({ isLoading: true, error: null });
        try {
            const deliveryId = await WebhookService.triggerWebhook(webhookId, payload);
            return deliveryId;
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to trigger webhook';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getDeliveries: async (webhookId, params) => {
        set({ isLoading: true, error: null });
        try {
            const deliveries = await WebhookService.getDeliveries(webhookId, params);
            set({ deliveries });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch deliveries';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getDeliveryDetails: async (deliveryId) => {
        set({ isLoading: true, error: null });
        try {
            return await WebhookService.getDeliveryDetails(deliveryId);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch delivery details';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    retryDelivery: async (deliveryId) => {
        set({ isLoading: true, error: null });
        try {
            await WebhookService.retryDelivery(deliveryId);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to retry delivery';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    verifySignature: async (webhookId, payload, signature) => {
        set({ isLoading: true, error: null });
        try {
            return await WebhookService.verifySignature(webhookId, payload, signature);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to verify signature';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getWebhookHealth: async (webhookId) => {
        set({ isLoading: true, error: null });
        try {
            const health = await WebhookService.getWebhookHealth(webhookId);
            set({ webhookHealth: health });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch webhook health';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    }
}))