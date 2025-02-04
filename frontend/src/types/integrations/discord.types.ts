
export enum DiscordMessageType {
    DEFAULT = "default",
    REPLY = "reply",
    EMBED = "embed"
}

export enum DiscordChannelType {
    TEXT = "text",
    VOICE = "voice",
    CATEGORY = "category",
    ANNOUNCEMENT = "announcement",
    FORUM = "forum"
}

export interface EmbedField {
    name: string;
    value: string;
    inline?: boolean;
}

export interface EmbedFooter {
    text: string;
    icon_url?: string;
}

export interface MessageEmbed {
    title?: string;
    description?: string;
    url?: string;
    color?: number;
    fields?: EmbedField[];
    footer?: EmbedFooter;
    timestamp?: string;
}

export interface DiscordMessage {
    content?: string;
    embed?: MessageEmbed;
    tts?: boolean;
    message_reference?: { [key: string]: string };  // For replies
}

export interface ChannelCreate {
    name: string;
    type: DiscordChannelType;
    topic?: string;
    parent_id?: string;  // Category ID
    nsfw?: boolean;
}

// Response types
export interface SendMessageResponse {
    message_id: string;
    channel_id: string;
    content?: string;
    timestamp: string;
}

export interface EditMessageResponse {
    message_id: string;
    content?: string;
    edited_timestamp: string;
}

export interface ChannelResponse {
    channel_id: string;
    name: string;
    type: string;
    position: number;
}

export interface ThreadResponse {
    thread_id: string;
    name: string;
    parent_id: string;
    owner_id: string;
}

export interface DiscordChannelMessage {
    id: string;
    content?: string;
    author: any;
    timestamp: string;
    embeds: any[];
}