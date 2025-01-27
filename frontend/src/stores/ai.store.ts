import { create } from 'zustand';
import { AIService } from '@/services/ai-service';
import { AIConfig, AIModel, AITask, CostEstimate } from '@/types/ai.types';

interface AIState {
   // State
   tasks: AITask[];
   currentTask: AITask | null;
   models: AIModel[];
   isLoading: boolean;
   error: string | null;

   // Actions
   setCurrentTask: (task: AITask) => void;
   clearError: () => void;
   
   // Service calls
   processAI: (config: AIConfig) => Promise<string>;
   processBatch: (configs: AIConfig[]) => Promise<string[]>;
   getModels: () => Promise<void>;
   estimateCost: (config: AIConfig) => Promise<CostEstimate>;
   getTaskStatus: (taskId: string) => Promise<void>;
   listTasks: (params?: {
       workflow_id?: string;
       status?: string;
       limit?: number;
       offset?: number;
   }) => Promise<void>;
   cancelTask: (taskId: string) => Promise<void>;
   retryTask: (taskId: string) => Promise<void>;
}

export const useAIStore = create<AIState>((set) => ({
   tasks: [],
   currentTask: null,
   models: [],
   isLoading: false,
   error: null,

   setCurrentTask: (task) => set({ currentTask: task }),
   clearError: () => set({ error: null }),

   processAI: async (config) => {
       set({ isLoading: true, error: null });
       try {
           const taskId = await AIService.processAI(config);
           return taskId;
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to process AI request';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   processBatch: async (configs) => {
       set({ isLoading: true, error: null });
       try {
           return await AIService.processBatch(configs);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to process batch';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getModels: async () => {
       set({ isLoading: true, error: null });
       try {
           const models = await AIService.getModels();
           set({ models });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to fetch models';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   estimateCost: async (config) => {
       set({ isLoading: true, error: null });
       try {
           return await AIService.estimateCost(config);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to estimate cost';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getTaskStatus: async (taskId) => {
       set({ isLoading: true, error: null });
       try {
           const task = await AIService.getTaskStatus(taskId);
           set({ currentTask: task });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to fetch task status';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   listTasks: async (params) => {
       set({ isLoading: true, error: null });
       try {
           const tasks = await AIService.listTasks(params);
           set({ tasks });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to fetch tasks';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   cancelTask: async (taskId) => {
       set({ isLoading: true, error: null });
       try {
           await AIService.cancelTask(taskId);
           set(state => ({
               tasks: state.tasks.map(task => 
                   task.workflow_id === taskId ? { ...task, status: 'cancelled' } : task
               ),
               currentTask: state.currentTask?.workflow_id === taskId ? 
                   { ...state.currentTask, status: 'cancelled' } : 
                   state.currentTask
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to cancel task';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   retryTask: async (taskId) => {
       set({ isLoading: true, error: null });
       try {
           await AIService.retryTask(taskId);
           set(state => ({
               tasks: state.tasks.map(task =>
                   task.workflow_id === taskId ? { ...task, status: 'pending' } : task
               ),
               currentTask: state.currentTask?.workflow_id === taskId ?
                   { ...state.currentTask, status: 'pending' } :
                   state.currentTask
           }));
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to retry task';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   }
}));