export enum EventStatus {
    CONFIRMED = "confirmed",
    TENTATIVE = "tentative",
    CANCELLED = "cancelled"
 }
 
 export enum CalendarActionType {
    CREATE_EVENT = "create_event",
    UPDATE_EVENT = "update_event",
    DELETE_EVENT = "delete_event",
    GET_EVENTS = "get_events",
    WATCH_EVENTS = "watch_events"
 }
 
 export interface Attendee {
    email: string;
    optional?: boolean;
    response_status?: string;
 }
 
 export interface EventReminder {
    method: "email" | "popup";
    minutes: number;
 }
 
 export interface EventTime {
    start_time: string; // ISO datetime
    end_time: string;  // ISO datetime
    timezone?: string;
 }
 
 export interface CalendarEvent {
    summary: string;
    description?: string;
    location?: string;
    time: EventTime;
    attendees?: Attendee[];
    reminders?: EventReminder[];
    recurrence?: string[]; // RRULE strings
    conference_data?: any;
    color_id?: string;
 }
 
 export interface CreateEventRequest extends CalendarEvent {
    calendar_id?: string;
 }
 
 export interface UpdateEventRequest extends CalendarEvent {
    calendar_id?: string;
 }
 
 export interface WatchRequest {
    channel_id: string;
    webhook_url: string;
    calendar_id?: string;
 }
 
 export interface WatchResponse {
    channel_id: string;
    resource_id: string;
    expiration: string;
 }
 
 export interface CalendarEventResponse {
    id: string;
    summary: string;
    description: string;
    location: string;
    start: string;
    end: string;
    status: string;
    html_link: string;
    created: string;
    updated: string;
    attendees: Attendee[];
    organizer: any;
    recurrence: string[];
    conference_data: any;
 }