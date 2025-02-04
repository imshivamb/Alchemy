
export enum SlackActionType {
    SEND_MESSAGE = "send_message",
    UPDATE_MESSAGE = "update_message",
    DELETE_MESSAGE = "delete_message",
    CREATE_CHANNEL = "create_channel",
    INVITE_USER = "invite_user",
    UPLOAD_FILE = "upload_file"
}

export enum SlackEventType {
    MESSAGE = "message",
    REACTION_ADDED = "reaction_added",
    CHANNEL_CREATED = "channel_created",
    CHANNEL_ARCHIVED = "channel_archived",
    MEMBER_JOINED_CHANNEL = "member_joined_channel",
    FILE_SHARED = "file_shared",
    APP_MENTION = "app_mention"
}

export interface MessageBlock {
    type: string;
    text?: { [key: string]: string };
    elements?: any[];
    accessory?: any;
}

export interface SlackMessage {
    channel: string;
    text?: string;
    blocks?: MessageBlock[];
    thread_ts?: string;
    reply_broadcast?: boolean;
    unfurl_links?: boolean;
    unfurl_media?: boolean;
    mrkdwn?: boolean;
}

export interface FileUpload {
    channels: string[];
    content?: string;
    file_path?: string;
    filename: string;
    filetype?: string;
    initial_comment?: string;
    thread_ts?: string;
}

export interface ChannelCreate {
    name: string;
    is_private?: boolean;
    team_id?: string;
}

export interface UserInvite {
    channel: string;
    users: string[];
}

export interface SlackResponse {
    ok: boolean;
    error?: string;
    warning?: string;
    response_metadata?: any;
}

export interface SlackEvent {
    type: SlackEventType;
    event_id: string;
    team_id: string;
    event_time: number;
    event_data: any;
}

// API Response types
export interface SendMessageResponse {
    message_id: string;
    channel: string;
    message: any;
}

export interface CreateChannelResponse {
    channel_id: string;
    name: string;
    is_private: boolean;
}

export interface FileUploadResponse {
    file_id: string;
    url: string;
    permalink: string;
}

export interface UpdateMessageResponse {
    message_ts: string;
    channel: string;
    text?: string;
    blocks?: MessageBlock[];
}