
import axiosInstance from "@/lib/axios/axios-instance";
import {
   CalendarEventResponse,
   CreateEventRequest,
   UpdateEventRequest,
   WatchRequest,
   WatchResponse
} from "@/types/integrations/calendar.types";
import axios, { AxiosResponse } from "axios";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';
const CALENDAR_BASE = `${FASTAPI_BASE_URL}/integrations/calendar`;

export class CalendarService {
   static async createEvent(event: CreateEventRequest): Promise<CalendarEventResponse> {
       try {
           const response: AxiosResponse<CalendarEventResponse> = await axiosInstance.post(
               `${CALENDAR_BASE}/events`,
               event
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to create event');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async updateEvent(eventId: string, event: UpdateEventRequest): Promise<CalendarEventResponse> {
       try {
           const response: AxiosResponse<CalendarEventResponse> = await axiosInstance.put(
               `${CALENDAR_BASE}/events/${eventId}`,
               event
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to update event');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async deleteEvent(eventId: string, calendarId: string = 'primary'): Promise<void> {
       try {
           await axiosInstance.delete(
               `${CALENDAR_BASE}/events/${eventId}`,
               { params: { calendar_id: calendarId } }
           );
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to delete event');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async listEvents(params: {
       calendar_id?: string;
       time_min?: string;
       time_max?: string;
       q?: string;
       max_results?: number;
   }): Promise<CalendarEventResponse[]> {
       try {
           const response: AxiosResponse<CalendarEventResponse[]> = await axiosInstance.get(
               `${CALENDAR_BASE}/events`,
               { params }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to list events');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async watchEvents(request: WatchRequest): Promise<WatchResponse> {
       try {
           const response: AxiosResponse<WatchResponse> = await axiosInstance.post(
               `${CALENDAR_BASE}/watch`,
               request
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to setup watch');
           }
           throw new Error('An unexpected error occurred');
       }
   }
}