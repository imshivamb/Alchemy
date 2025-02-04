// services/discord.service.ts

import axiosInstance from "@/lib/axios/axios-instance";
import {
   DiscordMessage,
   ChannelCreate,
   SendMessageResponse,
   EditMessageResponse,
   ChannelResponse,
   ThreadResponse,
   DiscordChannelMessage
} from "@/types/integrations/discord.types";
import axios, { AxiosResponse } from "axios";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';
const DISCORD_BASE = `${FASTAPI_BASE_URL}/integrations/discord/discord`;

export class DiscordService {
   static async sendMessage(channelId: string, message: DiscordMessage): Promise<SendMessageResponse> {
       try {
           const response: AxiosResponse<SendMessageResponse> = await axiosInstance.post(
               `${DISCORD_BASE}/channels/${channelId}/messages`,
               message
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to send message');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getMessages(
       channelId: string,
       limit: number = 50,
       before?: string,
       after?: string
   ): Promise<DiscordChannelMessage[]> {
       try {
           const response: AxiosResponse<DiscordChannelMessage[]> = await axiosInstance.get(
               `${DISCORD_BASE}/channels/${channelId}/messages`,
               { params: { limit, before, after } }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to get messages');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async createChannel(guildId: string, channel: ChannelCreate): Promise<ChannelResponse> {
       try {
           const response: AxiosResponse<ChannelResponse> = await axiosInstance.post(
               `${DISCORD_BASE}/guilds/${guildId}/channels`,
               channel
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to create channel');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getGuildChannels(guildId: string): Promise<ChannelResponse[]> {
       try {
           const response: AxiosResponse<ChannelResponse[]> = await axiosInstance.get(
               `${DISCORD_BASE}/guilds/${guildId}/channels`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to get guild channels');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async editMessage(
       channelId: string,
       messageId: string,
       message: DiscordMessage
   ): Promise<EditMessageResponse> {
       try {
           const response: AxiosResponse<EditMessageResponse> = await axiosInstance.patch(
               `${DISCORD_BASE}/channels/${channelId}/messages/${messageId}`,
               message
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to edit message');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async addReaction(channelId: string, messageId: string, emoji: string): Promise<boolean> {
       try {
           const response: AxiosResponse<{success: boolean}> = await axiosInstance.put(
               `${DISCORD_BASE}/channels/${channelId}/messages/${messageId}/reactions/${emoji}`
           );
           return response.data.success;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to add reaction');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async createThread(
       channelId: string,
       name: string,
       messageId?: string,
       autoArchiveDuration: number = 1440
   ): Promise<ThreadResponse> {
       try {
           const response: AxiosResponse<ThreadResponse> = await axiosInstance.post(
               `${DISCORD_BASE}/channels/${channelId}/threads`,
               { name, message_id: messageId, auto_archive_duration: autoArchiveDuration }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to create thread');
           }
           throw new Error('An unexpected error occurred');
       }
   }
}