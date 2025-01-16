export interface Workspace {
    id: string;
    name: string;
    role: 'admin' | 'member';
    is_owner: boolean;
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
    workspaces: Workspace[];
    onWorkspaceChange?: (workspaceId: string) => void;
}

export interface WorkspaceMember {
    id: string;
    user: {
        id: string;
        email: string;
        first_name: string;
        last_name: string;
    };
    workspace: string;
    role: 'admin' | 'member';
    joined_at: string;
    invited_by: {
        id: string;
        email: string;
        first_name: string;
        last_name: string;
    };
}

export interface CreateWorkspaceData {
    name: string;
}

export interface AddWorkspaceMemberData {
    email: string;
    role: 'admin' | 'member';
}