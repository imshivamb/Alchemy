export enum AIModelType {
    GPT_40_MINI = 'GPT_40_MINI',
    GPT_4 = 'GPT_4',
    GPT_35_TURBO = 'GPT_35_TURBO'
}

export enum PreprocessorType {
    SUMMARIZE = 'SUMMARIZE',
    TRANSLATE = 'TRANSLATE',
    EXTRACT = 'EXTRACT',
    FORMAT = 'FORMAT'
}

export enum OutputFormat {
    TEXT = 'TEXT',
    JSON = 'JSON',
    MARKDOWN = 'MARKDOWN',
    HTML = 'HTML'
}

export interface AIConfig {
    model: AIModelType;
    prompt: string;
    system_message?: string;
    temperature?: number;
    max_tokens?: number;
    preprocessors?: Array<{
        type: PreprocessorType;
        target_language?: string;
        fields?: string[];
        format_type?: string;
    }>;
    output_format: OutputFormat;
    fallback_behavior?: any;
}

export interface AITask {
    id: string;
    workflow_id: string;
    user_id: string;
    config: AIConfig;
    status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
    created_at: string;
    updated_at?: string;
    result?: any;
    error?: string;
    usage?: any;
}

export interface AIModel {
    id: AIModelType;
    name: string;
    max_tokens: number;
    supports_functions: boolean;
    cost_per_token: number;
    recommended_uses: string[];
}

export interface CostEstimate {
    estimated_tokens: number;
    estimated_cost: number;
}