export interface ChangePasswordData {
    current_password: string;
    new_password: string;
    confirm_new_password: string;
}

export interface Session {
    id: string;
    device: string;
    last_active: string;
    ip_address: string;
    location?: string;
    is_current: boolean;
}

export interface ApiKeyBasic {
    id: string;
    name: string;
    created_at: string;
    is_active: boolean;
}