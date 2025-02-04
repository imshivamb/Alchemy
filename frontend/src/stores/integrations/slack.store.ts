// stores/slack.store.ts

import { create } from 'zustand';
import { SlackService } from '@/services/integrations/slack-service';
import {
   SlackMessage,
   FileUpload,
   ChannelCreate, 
   MessageBlock,
   SlackEventType,
   SendMessageResponse,
   UpdateMessageResponse,
} from '@/types/integrations/slack.types';

interface SlackState {
   // State
   messages: (SendMessageResponse | UpdateMessageResponse)[];
   currentMessage: SendMessageResponse | UpdateMessageResponse | null;
   isLoading: boolean;
   error: string | null;

   // Basic actions
   setCurrentMessage: (message: SendMessageResponse) => void;
   clearError: () => void;

   // API actions
   sendMessage: (message: SlackMessage) => Promise<void>;
   createChannel: (channel: ChannelCreate) => Promise<void>;
   uploadFile: (file: FileUpload) => Promise<void>;
   updateMessage: (channel: string, messageTs: string, message: SlackMessage, blocks?: MessageBlock[]) => Promise<void>;
   addReaction: (channel: string, timestamp: string, emoji: string) => Promise<void>;
   getChannelInfo: (channelId: string) => Promise<void>;
   inviteToChannel: (channelId: string, userIds: string[]) => Promise<void>;
   subscribeToEvents: (callbackUrl: string, events: SlackEventType[]) => Promise<void>;
}

export const useSlackStore = create<SlackState>((set) => ({
   messages: [],
   currentMessage: null,
   isLoading: false,
   error: null,

   setCurrentMessage: (message) => set({ currentMessage: message }),
   clearError: () => set({ error: null }),

   sendMessage: async (message) => {
       set({ isLoading: true, error: null });
       try {
           const response = await SlackService.sendMessage(message);
           set(state => ({
               messages: [...state.messages, response],
               currentMessage: response
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   createChannel: async (channel) => {
       set({ isLoading: true, error: null });
       try {
           await SlackService.createChannel(channel);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to create channel';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   uploadFile: async (file) => {
       set({ isLoading: true, error: null });
       try {
           await SlackService.uploadFile(file);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to upload file';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   updateMessage: async (channel, messageTs, message, blocks) => {
    set({ isLoading: true, error: null });
    try {
        const updatedMessage = await SlackService.updateMessage(channel, messageTs, message, blocks);
        set(state => ({
            messages: state.messages.map(msg => 
                // For SendMessageResponse type
                'message_id' in msg 
                    ? msg.message_id === messageTs ? updatedMessage : msg
                    // For UpdateMessageResponse type
                    : msg.message_ts === messageTs ? updatedMessage : msg
            ),
            currentMessage: state.currentMessage 
                ? ('message_id' in state.currentMessage 
                    ? state.currentMessage.message_id === messageTs 
                    : state.currentMessage.message_ts === messageTs)
                    ? updatedMessage 
                    : state.currentMessage
                : null
        }));
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to update message';
        set({ error: errorMessage });
        throw error;
    } finally {
        set({ isLoading: false });
    }
 },

   addReaction: async (channel, timestamp, emoji) => {
       set({ isLoading: true, error: null });
       try {
           await SlackService.addReaction(channel, timestamp, emoji);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to add reaction';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getChannelInfo: async (channelId) => {
       set({ isLoading: true, error: null });
       try {
           await SlackService.getChannelInfo(channelId);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to get channel info';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   inviteToChannel: async (channelId, userIds) => {
       set({ isLoading: true, error: null });
       try {
           await SlackService.inviteToChannel(channelId, userIds);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to invite users';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   subscribeToEvents: async (callbackUrl, events) => {
       set({ isLoading: true, error: null });
       try {
           await SlackService.subscribeToEvents(callbackUrl, events);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to subscribe to events';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   }
}));