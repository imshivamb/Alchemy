export interface Workflow {
    id: number;
    name: string;
    description?: string;
    created_by: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
    workflow_data: any;
    tasks: WorkflowTask[];
    webhooks: Webhook[];
    workflow_limits: WorkflowLimits;
    task_count: number;
    webhook_count: number;
}

export interface WorkflowTask {
    id: number;
    name: string;
    task_type: 'trigger' | 'action' | 'condition' | 'transformer' | 'ai_process';
    config: any;
    order: number;
    is_active: boolean;
    workflow: number;
}

export interface Webhook {
    id: string;
    name: string;
    workflow: number;
    webhook_type: 'trigger' | 'action';
    trigger_url?: string;
    secret_key?: string;
    target_url?: string;
    http_method: string;
    headers: Record<string, string>;
    created_by: string;
    created_at: string;
    is_active: boolean;
    config: any;
    logs: WebhookLog[];
}

export interface WebhookLog {
    id: number;
    webhook: string;
    timestamp: string;
    request_method: string;
    request_headers: Record<string, string>;
    request_body: any;
    response_status?: number;
    response_body?: any;
    error_message?: string;
}

export interface WorkflowLimits {
    plan: string;
    total_limit: number;
    current_count: number;
    remaining: number;
}

export interface CreateWorkflowData {
    name: string;
    description?: string;
    is_active?: boolean;
    workflow_data: any;
}