// services/sheets.service.ts

import axiosInstance from "@/lib/axios/axios-instance";
import { 
   SpreadsheetCreate,
   CreateSpreadsheetResponse, 
   RangeData,
   ValueInputOption,
   ValueRenderOption,
   UpdateResponse,
   AppendResponse,
   ClearResponse,
   SpreadsheetMetadata
} from "@/types/integrations/sheets.types";
import axios, { AxiosResponse } from "axios";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';
const SHEETS_BASE = `${FASTAPI_BASE_URL}/integrations/sheets`;

export class SheetsService {
   static async createSpreadsheet(data: SpreadsheetCreate): Promise<CreateSpreadsheetResponse> {
       try {
           const response: AxiosResponse<CreateSpreadsheetResponse> = await axiosInstance.post(
               `${SHEETS_BASE}/spreadsheets`,
               data
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to create spreadsheet');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getValues(
       spreadsheetId: string, 
       range: string,
       renderOption: ValueRenderOption = ValueRenderOption.FORMATTED_VALUE
   ): Promise<any[][]> {
       try {
           const response: AxiosResponse<{values: any[][]}> = await axiosInstance.get(
               `${SHEETS_BASE}/spreadsheets/${spreadsheetId}/values/${range}`,
               { params: { render_option: renderOption } }
           );
           return response.data.values;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to get values');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async updateValues(
       spreadsheetId: string,
       rangeData: RangeData,
       inputOption: ValueInputOption = ValueInputOption.USER_ENTERED
   ): Promise<UpdateResponse> {
       try {
           const response: AxiosResponse<UpdateResponse> = await axiosInstance.put(
               `${SHEETS_BASE}/spreadsheets/${spreadsheetId}/values`,
               rangeData,
               { params: { input_option: inputOption } }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to update values');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async appendValues(
       spreadsheetId: string,
       rangeData: RangeData,
       inputOption: ValueInputOption = ValueInputOption.USER_ENTERED
   ): Promise<AppendResponse> {
       try {
           const response: AxiosResponse<AppendResponse> = await axiosInstance.post(
               `${SHEETS_BASE}/spreadsheets/${spreadsheetId}/values:append`,
               rangeData,
               { params: { input_option: inputOption } }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to append values');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async clearValues(spreadsheetId: string, range: string): Promise<ClearResponse> {
       try {
           const response: AxiosResponse<ClearResponse> = await axiosInstance.post(
               `${SHEETS_BASE}/spreadsheets/${spreadsheetId}/values/${range}:clear`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to clear values');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async getSpreadsheetMetadata(spreadsheetId: string): Promise<SpreadsheetMetadata> {
       try {
           const response: AxiosResponse<SpreadsheetMetadata> = await axiosInstance.get(
               `${SHEETS_BASE}/spreadsheets/${spreadsheetId}`
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to get metadata');
           }
           throw new Error('An unexpected error occurred');
       }
   }

   static async batchUpdate(spreadsheetId: string, requests: any[]): Promise<any> {
       try {
           const response: AxiosResponse<any> = await axiosInstance.post(
               `${SHEETS_BASE}/spreadsheets/${spreadsheetId}:batchUpdate`,
               { requests }
           );
           return response.data;
       } catch (error) {
           if (axios.isAxiosError(error)) {
               throw new Error(error.response?.data?.detail || 'Failed to perform batch update');
           }
           throw new Error('An unexpected error occurred');
       }
   }
}