export interface Workspace {
    id: string;
    name: string;
    owner: string;
    plan_type: 'free' | 'business' | 'enterprise';
    settings: WorkspaceSettings;
    created_at: string;
    updated_at: string;
}

export interface WorkspaceSettings {
    default_timezone?: string;
    notification_preferences?: {
        email: boolean;
        slack?: boolean;
    };
    workflow_settings?: {
        auto_retry: boolean;
        max_retries?: number;
    };
}

export interface WorkspaceStats {
    plan: string;
    members: {
        total: number;
        limit: number;
    };
    teams: {
        total: number;
        limit: number;
    };
}

export interface UpdateWorkspaceData {
    name?: string;
    settings?: Partial<WorkspaceSettings>;
}

export interface WorkspaceSwitcherProps {
    workspaces: {
      id: string;
      name: string;
      role: string;
      is_owner: boolean;
      plan_type: 'free' | 'business' | 'enterprise';
    }[];
    onWorkspaceChange?: (workspaceId: string) => void;
}