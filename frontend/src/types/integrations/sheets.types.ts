
export enum SheetsActionType {
    READ = "read",
    WRITE = "write", 
    APPEND = "append",
    CLEAR = "clear",
    CREATE = "create"
 }
 
 export enum ValueInputOption {
    RAW = "raw",
    USER_ENTERED = "user_entered"
 }
 
 export enum ValueRenderOption {
    FORMATTED_VALUE = "formatted_value",
    UNFORMATTED_VALUE = "unformatted_value", 
    FORMULA = "formula"
 }
 
 export interface RangeData {
    range: string;
    values: any[][];
 }
 
 export interface SheetProperties {
    title: string;
    sheet_type?: string;
    row_count?: number;
    column_count?: number;
 }
 
 export interface SpreadsheetCreate {
    title: string;
    sheets: SheetProperties[];
 }
 
 export interface SpreadsheetMetadata {
    spreadsheet_id: string;
    title: string;
    locale: string;
    time_zone: string;
    sheets: {
        sheet_id: string;
        title: string;
        index: number;
        sheet_type: string;
        grid_properties: any;
    }[];
 }
 
 export interface UpdateResponse {
    updated_cells: number;
    updated_rows: number;
    updated_columns: number;
    updated_range: string;
 }
 
 export interface AppendResponse {
    updates: {
        spreadsheet_id: string;
        updated_range: string;
        updated_rows: number;
        updated_columns: number;
    };
 }
 
 export interface ClearResponse {
    cleared_range: string;
 }
 
 export interface CreateSpreadsheetResponse {
    spreadsheet_id: string;
    title: string;
    sheets: {
        sheet_id: string;
        title: string;
    }[];
    spreadsheet_url: string;
 }