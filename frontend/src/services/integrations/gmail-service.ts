
import axiosInstance from "@/lib/axios/axios-instance";
import { 
   EmailMessage,
   GmailMessage,
   GmailFilter,
   SendEmailResponse,
   UpdateLabelsRequest,
   UpdateLabelsResponse,
   WatchRequest,
   WatchResponse,
   GmailLabel
} from "@/types/integrations/gmail.types";
import axios, { AxiosResponse } from "axios";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';
const GMAIL_BASE = `${FASTAPI_BASE_URL}/integrations/gmail`;

export class GmailService {
   static async sendEmail(message: EmailMessage): Promise<SendEmailResponse> {
       try {
           const response: AxiosResponse<SendEmailResponse> = await axiosInstance.post(
               `${GMAIL_BASE}/send`,
               message
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to send email');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async readEmails(filter: GmailFilter, maxResults: number = 10): Promise<GmailMessage[]> {
       try {
           const response: AxiosResponse<GmailMessage[]> = await axiosInstance.post(
               `${GMAIL_BASE}/read`,
               { filter, max_results: maxResults }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to read emails');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getMessage(messageId: string): Promise<GmailMessage> {
       try {
           const response: AxiosResponse<GmailMessage> = await axiosInstance.get(
               `${GMAIL_BASE}/messages/${messageId}`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to get message');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async updateLabels(request: UpdateLabelsRequest): Promise<UpdateLabelsResponse> {
       try {
           const response: AxiosResponse<UpdateLabelsResponse> = await axiosInstance.post(
               `${GMAIL_BASE}/labels`,
               request
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to update labels');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getLabels(): Promise<GmailLabel[]> {
       try {
           const response: AxiosResponse<GmailLabel[]> = await axiosInstance.get(
               `${GMAIL_BASE}/labels`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to get labels');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async watchMailbox(request: WatchRequest): Promise<WatchResponse> {
       try {
           const response: AxiosResponse<WatchResponse> = await axiosInstance.post(
               `${GMAIL_BASE}/watch`,
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

   static async stopWatching(): Promise<void> {
       try {
           await axiosInstance.post(`${GMAIL_BASE}/watch/stop`);
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to stop watching');
           }
           throw new Error('An unexpected error occurred');
       }
   }
}