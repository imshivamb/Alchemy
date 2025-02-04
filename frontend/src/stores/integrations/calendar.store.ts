
import { create } from 'zustand';
import { CalendarService } from '@/services/integrations/calendar-service';
import {
   CalendarEventResponse,
   CreateEventRequest,
   UpdateEventRequest,
   WatchRequest
} from '@/types/integrations/calendar.types';

interface CalendarState {
   // State
   events: CalendarEventResponse[];
   currentEvent: CalendarEventResponse | null;
   isLoading: boolean;
   error: string | null;

   // Basic actions
   setCurrentEvent: (event: CalendarEventResponse) => void;
   clearError: () => void;

   // API actions
   createEvent: (event: CreateEventRequest) => Promise<void>;
   updateEvent: (eventId: string, event: UpdateEventRequest) => Promise<void>;
   deleteEvent: (eventId: string, calendarId?: string) => Promise<void>;
   listEvents: (params: {
       calendar_id?: string;
       time_min?: string;
       time_max?: string;
       q?: string;
       max_results?: number;
   }) => Promise<void>;
   watchEvents: (request: WatchRequest) => Promise<void>;
}

export const useCalendarStore = create<CalendarState>((set) => ({
   events: [],
   currentEvent: null,
   isLoading: false,
   error: null,

   setCurrentEvent: (event) => set({ currentEvent: event }),
   clearError: () => set({ error: null }),

   createEvent: async (event) => {
       set({ isLoading: true, error: null });
       try {
           const newEvent = await CalendarService.createEvent(event);
           set(state => ({
               events: [...state.events, newEvent],
               currentEvent: newEvent
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to create event';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   updateEvent: async (eventId, event) => {
       set({ isLoading: true, error: null });
       try {
           const updatedEvent = await CalendarService.updateEvent(eventId, event);
           set(state => ({
               events: state.events.map(e => 
                   e.id === eventId ? updatedEvent : e
               ),
               currentEvent: state.currentEvent?.id === eventId 
                   ? updatedEvent 
                   : state.currentEvent
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to update event';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   deleteEvent: async (eventId, calendarId = 'primary') => {
       set({ isLoading: true, error: null });
       try {
           await CalendarService.deleteEvent(eventId, calendarId);
           set(state => ({
               events: state.events.filter(e => e.id !== eventId),
               currentEvent: state.currentEvent?.id === eventId 
                   ? null 
                   : state.currentEvent
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to delete event';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   listEvents: async (params) => {
       set({ isLoading: true, error: null });
       try {
           const events = await CalendarService.listEvents(params);
           set({ events });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to list events';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   watchEvents: async (request) => {
       set({ isLoading: true, error: null });
       try {
           await CalendarService.watchEvents(request);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to setup watch';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   }
}));