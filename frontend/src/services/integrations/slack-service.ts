
import axiosInstance from "@/lib/axios/axios-instance";
import {
   SlackMessage,
   FileUpload,
   ChannelCreate,
   MessageBlock,
   SlackEventType,
   SendMessageResponse,
   CreateChannelResponse,
   FileUploadResponse,
   UpdateMessageResponse
} from "@/types/integrations/slack.types";
import axios, { AxiosResponse } from "axios";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';
const SLACK_BASE = `${FASTAPI_BASE_URL}/integrations/slack`;

export class SlackService {
   static async sendMessage(message: SlackMessage): Promise<SendMessageResponse> {
       try {
           const response: AxiosResponse<SendMessageResponse> = await axiosInstance.post(
               `${SLACK_BASE}/message`,
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

   static async createChannel(channel: ChannelCreate): Promise<CreateChannelResponse> {
       try {
           const response: AxiosResponse<CreateChannelResponse> = await axiosInstance.post(
               `${SLACK_BASE}/channels`,
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

   static async uploadFile(file: FileUpload): Promise<FileUploadResponse> {
       try {
           const response: AxiosResponse<FileUploadResponse> = await axiosInstance.post(
               `${SLACK_BASE}/files`,
               file
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to upload file');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async updateMessage(
       channel: string,
       messageTs: string,
       message: SlackMessage,
       blocks?: MessageBlock[]
   ): Promise<UpdateMessageResponse> {
       try {
           const response: AxiosResponse<UpdateMessageResponse> = await axiosInstance.put(
               `${SLACK_BASE}/messages/${channel}/${messageTs}`,
               { ...message, blocks }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to update message');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async addReaction(channel: string, timestamp: string, emoji: string): Promise<void> {
       try {
           await axiosInstance.post(`${SLACK_BASE}/reactions`, {
               channel,
               timestamp,
               emoji
           });
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to add reaction');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getChannelInfo(channelId: string): Promise<any> {
       try {
           const response: AxiosResponse<any> = await axiosInstance.get(
               `${SLACK_BASE}/channels/${channelId}`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to get channel info');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async inviteToChannel(channelId: string, userIds: string[]): Promise<any> {
       try {
           const response: AxiosResponse<any> = await axiosInstance.post(
               `${SLACK_BASE}/channels/${channelId}/invite`,
               { user_ids: userIds }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to invite users');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async subscribeToEvents(callbackUrl: string, events: SlackEventType[]): Promise<any> {
       try {
           const response: AxiosResponse<any> = await axiosInstance.post(
               `${SLACK_BASE}/events/subscribe`,
               { callback_url: callbackUrl, events }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to subscribe to events');
           }
           throw new Error('An unexpected error occurred');
       }
   }
}