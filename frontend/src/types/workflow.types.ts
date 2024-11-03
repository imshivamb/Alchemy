export type NodeType = 'action' | 'trigger' | 'condition';

// Base node interface
export interface Position {
    x: number;
    y: number;
}
export interface BaseNode {
    id: string;
    type: NodeType;
    position: Position;
    selected?: boolean;
    dragging?: boolean;
}

// Trigger Specific Types
export type WebhookMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
export type EmailFilter = 'subject' | 'from' | 'to' | 'body';
export type ScheduleType = 'cron' | 'interval' | 'specific-time';

export interface WebhookConfig {
    webhookUrl?: string;
    method: WebhookMethod;
    headers?: Record<string, string>;
    authentication?: {
        username?: string;
        password?: string;
        type?: 'none' | 'basic' | 'bearer' | 'api-key';
        token?: string;
        apiKey?: string;

    }
    retryConfig?: {
        maxRetries?: number;
        retryInterval?: number;
    }

}

export interface ScheduleConfig {
    scheduleType: ScheduleType;
    cronExpression?: string;
    interval?: {
      value: number;
      unit: 'minutes' | 'hours' | 'days';
    };
    specificTime?: {
      time: string;
      timezone: string;
      days: ('monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday')[];
    };
    timezone: string;
}

export interface EmailConfig {
    connectionId?: string; // Reference to stored email connection
    filters: {
      type: EmailFilter;
      value: string;
      condition: 'equals' | 'contains' | 'starts_with' | 'ends_with';
    }[];
    folders: string[];
    includeAttachments: boolean;
    markAsRead: boolean;
}

export interface TriggerNode extends BaseNode {
    type: 'trigger';
    data: {
      triggerType: 'webhook' | 'schedule' | 'email';
      label: string;
      description: string;
      isValid: boolean;
      errorMessage?: string;
      config: {
        webhook?: WebhookConfig;
        schedule?: ScheduleConfig;
        email?: EmailConfig;
      };
      outputSchema: {
        type: 'object';
        properties: Record<string, any>;
      };
    };
}

// Edge types for workflow connections
export interface WorkflowEdge {
    id: string;
    source: string;
    target: string;
    type?: 'default' | 'success' | 'failure';
    animated?: boolean;
    label?: string;
    style?: Record<string, any>;
  }
  
  // Validation Types
  export interface ValidationResult {
    isValid: boolean;
    errors: ValidationError[];
  }
  
  export interface ValidationError {
    nodeId: string;
    field: string;
    message: string;
  }


  //Action Node Types
  export type AIModelType = 'gpt-4' | 'gpt-3.5-turbo' | 'gpt-4o-mini' | 'claude-2';
  export type Web3Network = 'solana-mainnet' | 'solana-devnet' | 'solana-testnet';
  export type Web3ActionType = 'transfer' | 'mint' | 'burn' | 'stake' | 'unstake';

export interface AIConfig {
    model: AIModelType;
    customEndpoint?: string;
    maxTokens?: number;
    prompt?: string;
    temperature?: number;
    systemMessage?: string;
    outputFormat?: 'text' | 'json' | 'markdown';
    preprocessors?: {
        type: 'summarize' | 'translate' | 'extract';
        config: Record<string, any>;
    }[];
    fallbackBehavior?: {
        retryCount: number;
        fallbackModel?: AIModelType;
    };
}

export interface Web3Config {
    network: Web3Network;
    actionType: Web3ActionType;
    wallet?: string;
    amount?: string;
    recipient?: string;
    token?: {
      mint: string;
      decimals: number;
    };
    contractAddress?: string;
    functionName?: string;
    parameters?: Record<string, any>;
    gasConfig?: {
      priorityFee?: number;
      maxFee?: number;
    };
}

export interface HTTPConfig {
    url: string;
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    headers?: Record<string, string>;
    body?: string | Record<string, any>;
    authentication?: {
      type: 'none' | 'basic' | 'bearer' | 'api-key';
      credentials?: Record<string, string>;
    };
    retryConfig?: {
      maxRetries: number;
      retryInterval: number;
    };
    timeout?: number;
}

export interface DataTransformConfig {
    operations: {
      type: 'map' | 'filter' | 'reduce' | 'sort' | 'transform';
      field?: string;
      expression: string;
    }[];
    inputMapping: Record<string, string>;
    outputMapping: Record<string, string>;
    errorBehavior: 'skip' | 'fail' | 'default';
}

export interface ActionNode extends BaseNode {
    type: 'action';
    data: {
      actionType: 'ai' | 'web3' | 'http' | 'transform';
      label: string;
      description: string;
      isValid: boolean;
      errorMessage?: string;
      config: {
        ai?: AIConfig;
        web3?: Web3Config;
        http?: HTTPConfig;
        transform?: DataTransformConfig;
      };
      inputSchema: {
        type: 'object';
        properties: Record<string, any>;
        required: string[];
      };
      outputSchema: {
        type: 'object';
        properties: Record<string, any>;
      };
    };
  }

  // Condition Node Types
export type ConditionOperator = 
| 'equals' 
| 'not_equals' 
| 'greater_than' 
| 'less_than' 
| 'contains' 
| 'not_contains' 
| 'starts_with' 
| 'ends_with' 
| 'is_empty' 
| 'is_not_empty'
| 'matches_regex';

export interface ConditionRule {
    field: string;
    operator: ConditionOperator;
    value: any;
    valueType: 'string' | 'number' | 'boolean' | 'null' | 'array' | 'object';
}

export interface ConditionGroup {
    operator: 'and' | 'or';
    rules: (ConditionRule | ConditionGroup)[];
}

export interface ConditionNode extends BaseNode {
    type: 'condition';
    data: {
      label: string;
      description: string;
      isValid: boolean;
      errorMessage?: string;
      config: {
        condition: ConditionGroup;
        defaultPath: 'true' | 'false';
        customLogic?: string;
        timeout?: number;
      };
      inputSchema: {
        type: 'object';
        properties: Record<string, any>;
        required: string[];
      };
    };
}

  export type WorkflowNode = TriggerNode | ActionNode | ConditionNode;

