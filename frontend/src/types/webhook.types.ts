export enum WebhookMethod {
    GET = 'GET',
    POST = 'POST',
    PUT = 'PUT',
    PATCH = 'PATCH',
    DELETE = 'DELETE'
}

export enum WebhookStatus {
    ACTIVE = 'active',
    INACTIVE = 'inactive',
    FAILED = 'failed',
    DELETED = 'deleted',
    PENDING = 'pending'
}

export interface RetryStrategy {
    max_retries: number;
    initial_interval: number;
    max_interval: number;
    multiplier: number;
}

export interface WebhookConfig {
    url: string;
    method: WebhookMethod;
    headers: Record<string, string>;
    authentication?: Record<string, string>;
    retry_strategy: RetryStrategy;
    timeout: number;
    verify_ssl: boolean;
}

export interface WebhookSecret {
    key: string;
    header_name: string;
    hash_algorithm: string;
}

// Django Webhook Model
export interface BaseWebhook {
    id?: string;
    name: string;
    workflow: number;
    webhook_type: 'trigger' | 'action';
    trigger_url?: string;
    target_url?: string;
    http_method: string;
    headers: Record<string, string>;
    created_by?: string;
    created_at?: string;
    is_active?: boolean;
    config?: any;
  }

  export interface CreateWebhookResponse extends BaseWebhook {
    id: string;
    trigger_url: string;
  }
// FastAPI Extended Webhook
export interface FastAPIWebhook extends Omit<BaseWebhook, 'config'> {
    id: string;
    is_active: boolean;
    status: WebhookStatus;
    last_triggered?: string;
    total_deliveries: number;
    successful_deliveries: number;
    failed_deliveries: number;
    config: WebhookConfig;
    secret: WebhookSecret;
}

export interface WebhookDelivery {
    id: string;
    webhook_id: string;
    payload: any;
    status: string;
    headers: Record<string, string>;
    created_at: string;
    completed_at?: string;
    attempts: number;
    next_retry?: string;
    response?: any;
    error?: string;
}

export interface WebhookHealth {
    health_score: number;
    status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
    metrics: {
        total_deliveries: number;
        successful_deliveries: number;
        failed_deliveries: number;
        average_response_time: number;
        status_codes: Record<string, number>;
        error_types: Record<string, number>;
        retry_count: number;
    };
}