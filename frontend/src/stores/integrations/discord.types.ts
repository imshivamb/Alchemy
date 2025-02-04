// stores/discord.store.ts

import { create } from 'zustand';
import { DiscordService } from '@/services/integrations/discord-service';
import {
   DiscordMessage,
   ChannelCreate,
   ChannelResponse,
   DiscordChannelMessage
} from '@/types/integrations/discord.types';

interface DiscordState {
   // State
   messages: DiscordChannelMessage[];
   currentMessage: DiscordChannelMessage | null;
   channels: ChannelResponse[];
   isLoading: boolean;
   error: string | null;

   // Basic actions
   setCurrentMessage: (message: DiscordChannelMessage) => void;
   clearError: () => void;

   // API actions
   sendMessage: (channelId: string, message: DiscordMessage) => Promise<void>;
   getMessages: (channelId: string, limit?: number, before?: string, after?: string) => Promise<void>;
   createChannel: (guildId: string, channel: ChannelCreate) => Promise<void>;
   getGuildChannels: (guildId: string) => Promise<void>;
   editMessage: (channelId: string, messageId: string, message: DiscordMessage) => Promise<void>;
   addReaction: (channelId: string, messageId: string, emoji: string) => Promise<void>;
   createThread: (channelId: string, name: string, messageId?: string, autoArchiveDuration?: number) => Promise<void>;
}

export const useDiscordStore = create<DiscordState>((set) => ({
   messages: [],
   currentMessage: null,
   channels: [],
   isLoading: false,
   error: null,

   setCurrentMessage: (message) => set({ currentMessage: message }),
   clearError: () => set({ error: null }),

   sendMessage: async (channelId, message) => {
       set({ isLoading: true, error: null });
       try {
           const response = await DiscordService.sendMessage(channelId, message);
           set(state => ({
               messages: [...state.messages, { 
                   id: response.message_id,
                   content: response.content,
                   timestamp: response.timestamp,
                   author: {},  // TODO: add proper author info here
                   embeds: []
               }]
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getMessages: async (channelId, limit = 50, before, after) => {
       set({ isLoading: true, error: null });
       try {
           const messages = await DiscordService.getMessages(channelId, limit, before, after);
           set({ messages });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to get messages';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   createChannel: async (guildId, channel) => {
       set({ isLoading: true, error: null });
       try {
           const newChannel = await DiscordService.createChannel(guildId, channel);
           set(state => ({
               channels: [...state.channels, newChannel]
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to create channel';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getGuildChannels: async (guildId) => {
       set({ isLoading: true, error: null });
       try {
           const channels = await DiscordService.getGuildChannels(guildId);
           set({ channels });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to get guild channels';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   editMessage: async (channelId, messageId, message) => {
       set({ isLoading: true, error: null });
       try {
           const updatedMessage = await DiscordService.editMessage(channelId, messageId, message);
           set(state => ({
               messages: state.messages.map(msg => 
                   msg.id === messageId 
                       ? { 
                           ...msg, 
                           content: updatedMessage.content,
                           edited_timestamp: updatedMessage.edited_timestamp 
                       } 
                       : msg
               )
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to edit message';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   addReaction: async (channelId, messageId, emoji) => {
       set({ isLoading: true, error: null });
       try {
           await DiscordService.addReaction(channelId, messageId, emoji);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to add reaction';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   createThread: async (channelId, name, messageId, autoArchiveDuration) => {
       set({ isLoading: true, error: null });
       try {
           await DiscordService.createThread(channelId, name, messageId, autoArchiveDuration);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to create thread';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   }
}));