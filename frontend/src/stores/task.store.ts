import { create } from 'zustand';
import { TaskService } from '@/services/task-service';
import { WorkflowTask } from '@/types/workflow-api.types';

interface TaskState {
    // State
    tasks: WorkflowTask[];
    currentTask: WorkflowTask | null;
    isLoading: boolean;
    error: string | null;

    // Basic actions
    setCurrentTask: (task: WorkflowTask) => void;
    clearError: () => void;

    // API actions
    fetchTasks: () => Promise<void>;
    getTaskById: (taskId: number) => Promise<void>;
    createTask: (data: Partial<WorkflowTask>) => Promise<WorkflowTask>;
    updateTask: (taskId: number, data: Partial<WorkflowTask>) => Promise<void>;
    deleteTask: (taskId: number) => Promise<void>;
    
    // Workflow specific tasks
    getWorkflowTasks: (workflowId: number) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set) => ({
    tasks: [],
    currentTask: null,
    isLoading: false,
    error: null,

    setCurrentTask: (task) => set({ currentTask: task }),
    clearError: () => set({ error: null }),

    fetchTasks: async () => {
        set({ isLoading: true, error: null });
        try {
            const tasks = await TaskService.getTasks();
            set({ tasks });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch tasks';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getTaskById: async (taskId: number) => {
        set({ isLoading: true, error: null });
        try {
            const task = await TaskService.getTaskById(taskId);
            set(state => ({
                tasks: [...state.tasks.filter(t => t.id !== taskId), task],
                currentTask: state.currentTask?.id === taskId ? task : state.currentTask
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch task';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    createTask: async (data) => {
        set({ isLoading: true, error: null });
        try {
            const newTask = await TaskService.createTask(data);
            set(state => ({
                tasks: [...state.tasks, newTask]
            }));
            return newTask;
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to create task';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    updateTask: async (taskId, data) => {
        set({ isLoading: true, error: null });
        try {
            const updatedTask = await TaskService.updateTask(taskId, data);
            set(state => ({
                tasks: state.tasks.map(t => 
                    t.id === taskId ? updatedTask : t
                ),
                currentTask: state.currentTask?.id === taskId 
                    ? updatedTask 
                    : state.currentTask
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to update task';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    deleteTask: async (taskId) => {
        set({ isLoading: true, error: null });
        try {
            await TaskService.deleteTask(taskId);
            set(state => ({
                tasks: state.tasks.filter(t => t.id !== taskId),
                currentTask: state.currentTask?.id === taskId 
                    ? null 
                    : state.currentTask
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to delete task';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    // Get tasks for a specific workflow
    getWorkflowTasks: async (workflowId) => {
        set({ isLoading: true, error: null });
        try {
            const tasks = await TaskService.getTasks();
            const workflowTasks = tasks.filter(task => task.workflow === workflowId);
            set({ tasks: workflowTasks });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch workflow tasks';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    }
}))