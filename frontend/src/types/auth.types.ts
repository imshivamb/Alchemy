export interface RegisterData {
    email: string,
    password: string,
    confirm_password: string,
    first_name: string,
    last_name: string,
    phone_number?: string,
    organization?: string,
}

export interface LoginData {
    email: string,
    password: string
}


// Token types for authentication
export interface AuthTokens {
    access: string,
    refresh: string
}

//Notification preferences
export interface NotificationPreferences {
    email_notifications: boolean;
    workflow_notifications: boolean;
}

// Usage statistics
export interface UsageStats {
    last_login: string | null;
    registration_date: string;
}

export interface UserProfile {
    id: string;
    timezone: string;
    notification_preferences: NotificationPreferences;
    max_workflows: number;
    usage_stats: UsageStats;
    plan_type: string;
    onboarding_completed: boolean;
    account_status: string;
    created_at: string;
    updated_at: string;
}
export interface User {
    id: string,
    email: string,
    first_name: string,
    last_name: string,
    phone_number: string | null,
    organization: string | null,
    is_verified: boolean,
    created_at: string,
    updated_at: string,
    profile: UserProfile
}


// Full authentication response
export interface AuthResponse {
    tokens: AuthTokens;
    user: User;
  }

export interface PasswordResetConfirmData {
    token: string;
    password: string;
    confirm_password: string;
}

export interface EmailVerificationData {
    token: string;
}

export interface EmailVerificationStatus {
    is_verified: boolean;
}

export interface SocialAuthResponse {
    code: string;
    provider: 'google' | 'github';
}
  
export interface SocialAuthResult {
    tokens: AuthTokens;
    user: User;
}