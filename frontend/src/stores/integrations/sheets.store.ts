// stores/sheets.store.ts

import { create } from 'zustand';
import { SheetsService } from '@/services/integrations/sheets-service';
import {
   SpreadsheetCreate,
   RangeData,
   ValueInputOption,
   ValueRenderOption,
   SpreadsheetMetadata
} from '@/types/integrations/sheets.types';

interface SheetsState {
   // State
   currentSpreadsheet: SpreadsheetMetadata | null;
   currentValues: any[][] | null;
   isLoading: boolean;
   error: string | null;

   // Basic actions
   clearError: () => void;

   // API actions
   createSpreadsheet: (data: SpreadsheetCreate) => Promise<void>;
   getValues: (spreadsheetId: string, range: string, renderOption?: ValueRenderOption) => Promise<void>;
   updateValues: (spreadsheetId: string, rangeData: RangeData, inputOption?: ValueInputOption) => Promise<void>;
   appendValues: (spreadsheetId: string, rangeData: RangeData, inputOption?: ValueInputOption) => Promise<void>;
   clearValues: (spreadsheetId: string, range: string) => Promise<void>;
   getSpreadsheetMetadata: (spreadsheetId: string) => Promise<void>;
   batchUpdate: (spreadsheetId: string, requests: any[]) => Promise<void>;
}

export const useSheetsStore = create<SheetsState>((set) => ({
   currentSpreadsheet: null,
   currentValues: null,
   isLoading: false,
   error: null,

   clearError: () => set({ error: null }),

   createSpreadsheet: async (data) => {
    set({ isLoading: true, error: null });
    try {
        const response = await SheetsService.createSpreadsheet(data);
        set({
            currentSpreadsheet: {
                spreadsheet_id: response.spreadsheet_id,
                title: response.title,
                sheets: response.sheets.map(s => ({
                    sheet_id: s.sheet_id,
                    title: s.title,
                    index: 0,
                    sheet_type: 'GRID',
                    grid_properties: {}
                })),
                locale: 'en',
                time_zone: 'UTC'
            }
        });
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to create spreadsheet';
        set({ error: errorMessage });
        throw error;
    } finally {
        set({ isLoading: false });
    }
 },

   getValues: async (spreadsheetId, range, renderOption = ValueRenderOption.FORMATTED_VALUE) => {
       set({ isLoading: true, error: null });
       try {
           const values = await SheetsService.getValues(spreadsheetId, range, renderOption);
           set({ currentValues: values });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to get values';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   updateValues: async (spreadsheetId, rangeData, inputOption = ValueInputOption.USER_ENTERED) => {
       set({ isLoading: true, error: null });
       try {
           await SheetsService.updateValues(spreadsheetId, rangeData, inputOption);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to update values';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   appendValues: async (spreadsheetId, rangeData, inputOption = ValueInputOption.USER_ENTERED) => {
       set({ isLoading: true, error: null });
       try {
           await SheetsService.appendValues(spreadsheetId, rangeData, inputOption);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to append values';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   clearValues: async (spreadsheetId, range) => {
       set({ isLoading: true, error: null });
       try {
           await SheetsService.clearValues(spreadsheetId, range);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to clear values';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getSpreadsheetMetadata: async (spreadsheetId) => {
       set({ isLoading: true, error: null });
       try {
           const metadata = await SheetsService.getSpreadsheetMetadata(spreadsheetId);
           set({ currentSpreadsheet: metadata });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to get metadata';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   batchUpdate: async (spreadsheetId, requests) => {
       set({ isLoading: true, error: null });
       try {
           await SheetsService.batchUpdate(spreadsheetId, requests);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to perform batch update';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   }
}));