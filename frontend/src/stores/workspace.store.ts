import { create } from 'zustand';
import { WorkspaceService } from '@/services/workspace-service';
import { Workspace, CreateWorkspaceData, AddWorkspaceMemberData, WorkspaceStats } from '@/types/workspace.types';

interface WorkspaceState {
    // State
    currentWorkspace: Workspace | null;
    workspaces: Workspace[];
    isLoading: boolean;
    error: string | null;

    // Actions
    setCurrentWorkspace: (workspace: Workspace) => void;
    clearError: () => void;

    // API Actions
    fetchWorkspaces: () => Promise<void>;
    getWorkspaceById: (workspaceId: string) => Promise<void>;
    createWorkspace: (data: CreateWorkspaceData) => Promise<void>;
    deleteWorkspace: (workspaceId: string) => Promise<void>;
    updateWorkspace: (workspaceId: string, data: any) => Promise<void>;
    addWorkspaceMember: (workspaceId: string, data: AddWorkspaceMemberData) => Promise<void>;
    getWorkspaceStats: (workspaceId: string) => Promise<WorkspaceStats>;
}

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
    // Initial state
    currentWorkspace: null,
    workspaces: [],
    isLoading: false,
    error: null,

    // Basic actions
    setCurrentWorkspace: (workspace) => set({ currentWorkspace: workspace }),
    clearError: () => set({ error: null }),

    // API actions
    fetchWorkspaces: async () => {
        set({ isLoading: true, error: null });
        try {
            const workspaces = await WorkspaceService.getWorkspaces();
            set({ workspaces });

            // Set current workspace if not set
            const { currentWorkspace } = get();
            if (!currentWorkspace && workspaces.length > 0) {
                set({ currentWorkspace: workspaces[0] });
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch workspaces';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getWorkspaceById: async (workspaceId) => {
        set({ isLoading: true, error: null });
        try {
            const workspace = await WorkspaceService.getWorkspaceById(workspaceId);
            set(state => ({
                workspaces: [...state.workspaces.filter(w => w.id !== workspaceId), workspace]
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch workspace';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    createWorkspace: async (data) => {
        set({ isLoading: true, error: null });
        try {
            const newWorkspace = await WorkspaceService.createWorkspace(data);
            set(state => ({
                workspaces: [...state.workspaces, newWorkspace]
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to create workspace';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    deleteWorkspace: async (workspaceId) => {
        set({ isLoading: true, error: null });
        try {
            await WorkspaceService.deleteWorkspace(workspaceId);
            set(state => ({
                workspaces: state.workspaces.filter(w => w.id !== workspaceId),
                currentWorkspace: state.currentWorkspace?.id === workspaceId 
                    ? state.workspaces.find(w => w.id !== workspaceId) || null 
                    : state.currentWorkspace
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to delete workspace';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    updateWorkspace: async (workspaceId, data) => {
        set({ isLoading: true, error: null });
        try {
            const updatedWorkspace = await WorkspaceService.updateWorkspace(workspaceId, data);
            set(state => ({
                workspaces: state.workspaces.map(w => 
                    w.id === workspaceId ? updatedWorkspace : w
                ),
                currentWorkspace: state.currentWorkspace?.id === workspaceId 
                    ? updatedWorkspace 
                    : state.currentWorkspace
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to update workspace';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    addWorkspaceMember: async (workspaceId, data) => {
        set({ isLoading: true, error: null });
        try {
            await WorkspaceService.addWorkspaceMember(workspaceId, data);
            // Optionally refresh workspace data after adding member
            await get().getWorkspaceById(workspaceId);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to add workspace member';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getWorkspaceStats: async (workspaceId) => {
        set({ isLoading: true, error: null });
        try {
            const stats = await WorkspaceService.getWorkspaceStats(workspaceId);
            return stats;
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch workspace stats';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    }
}));