
export enum GmailActionType {
    SEND_EMAIL = "send_email",
    READ_EMAILS = "read_emails",
    WATCH_MAILBOX = "watch_mailbox", 
    UPDATE_LABELS = "update_labels"
 }
 
 export interface EmailAttachment {
    filename: string;
    content_type: string;
    data: string;  // Base64 encoded string
 }
 
 export interface EmailMessage {
    to: string[];
    subject: string;
    body: string;
    body_type: "text" | "html";
    cc?: string[];
    bcc?: string[];
    attachments?: EmailAttachment[];
 }
 
 export interface GmailFilter {
    from_?: string;
    to?: string;
    subject?: string;
    has_attachment?: boolean;
    label?: string;
    after?: string;
    before?: string;
 }
 
 export interface SendEmailRequest {
    to: string[];
    subject: string;
    body: string;
    body_type: "text" | "html";
    cc?: string[];
    bcc?: string[];
    attachments?: EmailAttachment[];
 }
 
 export interface SendEmailResponse {
    message_id: string;
    thread_id: string;
 }
 
 export interface ReadEmailsRequest {
    filter: GmailFilter;
    max_results?: number;
 }
 
 export interface GmailMessage {
    id: string;
    thread_id: string;
    subject: string;
    from: string;
    to: string;
    date: string;
    body: string;
    labels: string[];
 }
 
 export interface UpdateLabelsRequest {
    message_id: string;
    add_labels?: string[];
    remove_labels?: string[];
 }
 
 export interface UpdateLabelsResponse {
    message_id: string;
    labels: string[];
 }
 
 export interface WatchRequest {
    topic_name: string;
    label_ids?: string[];
 }
 
 export interface WatchResponse {
    history_id: string;
    expiration: string;
 }
 
 export interface GmailLabel {
    id: string;
    name: string;
    messageListVisibility?: string;
    labelListVisibility?: string;
    type?: string;
 }