import { create } from 'zustand';
import { WorkflowService } from '@/services/workflow-api-service';
import { Workflow, CreateWorkflowData, WorkflowLimits } from '@/types/workflow-api.types';
import axios from 'axios';

interface WorkflowApiState {
    // State
    workflows: Workflow[];
    currentWorkflow: Workflow | null;
    workflowLimits: WorkflowLimits | null;
    isLoading: boolean;
    error: string | null;

    // Basic actions
    setCurrentWorkflow: (workflow: Workflow) => void;
    clearError: () => void;

    // API actions
    fetchWorkflows: () => Promise<void>;
    getWorkflowById: (workflowId: number) => Promise<void>;
    createWorkflow: (data: CreateWorkflowData) => Promise<Workflow>;
    updateWorkflow: (workflowId: number, data: Partial<CreateWorkflowData>) => Promise<void>;
    deleteWorkflow: (workflowId: number) => Promise<void>;
    fetchWorkflowLimits: () => Promise<void>;
}

export const useWorkflowApiStore = create<WorkflowApiState>((set, get) => ({
    workflows: [],
    currentWorkflow: null,
    workflowLimits: null,
    isLoading: false,
    error: null,

    // Basic actions
    setCurrentWorkflow: (workflow) => set({ currentWorkflow: workflow }),
    clearError: () => set({ error: null }),

    // API actions
    fetchWorkflows: async() => {
        set({ isLoading: true, error: null });
        try {
            const workflows = await WorkflowService.getWorkflows();
            set({ workflows });

            const {currentWorkflow} = get();
            if (!currentWorkflow && workflows.length > 0) {
                set({ currentWorkflow: workflows[0] });
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch workflows';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getWorkflowById: async (workflowId: number) => {
        set({ isLoading: true, error: null });
        try {
            const workflow = await WorkflowService.getWorkflowById(workflowId);
            set(state => ({
                workflows: [...state.workflows.filter(w => w.id !== workflowId), workflow],
                currentWorkflow: state.currentWorkflow?.id === workflowId ? workflow : state.currentWorkflow
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch workflow';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    createWorkflow: async (data) => {
        set({ isLoading: true, error: null });
        try {
            const newWorkflow = await WorkflowService.createWorkflow(data);
            set(state => ({
                workflows: [...state.workflows, newWorkflow],
                currentWorkflow: newWorkflow
            }));
            return newWorkflow;
        } catch (error) {
            console.log('Store error:', error);
            if (axios.isAxiosError(error) && error.response?.status === 400) {
                throw error;
            }
            const errorMessage = error instanceof Error ? error.message : 'Failed to create workflow';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    updateWorkflow: async (workflowId: number, data) => {
        set({ isLoading: true, error: null });
        try {
            console.log('Updating workflow:', { workflowId, data });
            const updateWorkflow = await WorkflowService.updateWorkflow(workflowId, data);
            set(state => ({
                workflows: state.workflows.map(w => w.id === workflowId ? updateWorkflow : w),
                currentWorkflow: state.currentWorkflow?.id === workflowId ? updateWorkflow : state.currentWorkflow
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to update workflow';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    deleteWorkflow: async (workflowId: number) => {
        set({ isLoading: true, error: null });
        try {
            await WorkflowService.deleteWorkflow(workflowId);
            set(state => ({
                workflows: state.workflows.filter(w => w.id !== workflowId),
                currentWorkflow: state.currentWorkflow?.id === workflowId 
                ? state.workflows.find(w => w.id !== workflowId) || null 
                : state.currentWorkflow
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to delete workflow';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    fetchWorkflowLimits: async () => {
        set({ isLoading: true, error: null });
        try {
            const limits = await WorkflowService.getWorkflowLimits();
            set({ workflowLimits: limits });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch workflow limits';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    }
}))