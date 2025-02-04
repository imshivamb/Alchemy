// stores/gmail.store.ts

import { create } from 'zustand';
import { GmailService } from '@/services/integrations/gmail-service';
import { GmailMessage, EmailMessage, GmailFilter, GmailLabel, UpdateLabelsRequest, WatchRequest } from '@/types/integrations/gmail.types';

interface GmailState {
   // State
   messages: GmailMessage[];
   currentMessage: GmailMessage | null;
   labels: GmailLabel[];
   isLoading: boolean;
   error: string | null;

   // Basic actions
   setCurrentMessage: (message: GmailMessage) => void;
   clearError: () => void;

   // API actions
   sendEmail: (message: EmailMessage) => Promise<void>;
   readEmails: (filter: GmailFilter, maxResults?: number) => Promise<void>;
   getMessage: (messageId: string) => Promise<void>;
   updateLabels: (request: UpdateLabelsRequest) => Promise<void>;
   getLabels: () => Promise<void>;
   watchMailbox: (request: WatchRequest) => Promise<void>;
   stopWatching: () => Promise<void>;
}

export const useGmailStore = create<GmailState>((set) => ({
   messages: [],
   currentMessage: null,
   labels: [],
   isLoading: false,
   error: null,

   setCurrentMessage: (message) => set({ currentMessage: message }),
   clearError: () => set({ error: null }),

   sendEmail: async (message) => {
       set({ isLoading: true, error: null });
       try {
           await GmailService.sendEmail(message);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to send email';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   readEmails: async (filter, maxResults = 10) => {
       set({ isLoading: true, error: null });
       try {
           const messages = await GmailService.readEmails(filter, maxResults);
           set({ messages });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to read emails';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getMessage: async (messageId) => {
       set({ isLoading: true, error: null });
       try {
           const message = await GmailService.getMessage(messageId);
           set(state => ({
               messages: [...state.messages.filter(m => m.id !== messageId), message],
               currentMessage: message
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to get message';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   updateLabels: async (request) => {
       set({ isLoading: true, error: null });
       try {
           const result = await GmailService.updateLabels(request);
           set(state => ({
               messages: state.messages.map(m => 
                   m.id === request.message_id 
                       ? { ...m, labels: result.labels }
                       : m
               ),
               currentMessage: state.currentMessage?.id === request.message_id
                   ? { ...state.currentMessage, labels: result.labels }
                   : state.currentMessage
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to update labels';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getLabels: async () => {
       set({ isLoading: true, error: null });
       try {
           const labels = await GmailService.getLabels();
           set({ labels });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to get labels';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   watchMailbox: async (request) => {
       set({ isLoading: true, error: null });
       try {
           await GmailService.watchMailbox(request);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to setup watch';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   stopWatching: async () => {
       set({ isLoading: true, error: null });
       try {
           await GmailService.stopWatching();
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to stop watching';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   }
}));