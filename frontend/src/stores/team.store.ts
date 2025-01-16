import { TeamService } from '@/services/teams-service';
import { CreateTeamData, TeamDetail } from '@/types/teams.types';
import { create } from 'zustand';



interface TeamState {
    // State
    teams: TeamDetail[];
    currentTeam: TeamDetail | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    setCurrentTeam: (team: TeamDetail | null) => void;
    clearError: () => void;

    // API Actions
    fetchTeams: (workspaceId: string) => Promise<void>;
    getTeamById: (teamId: string) => Promise<void>;
    createTeam: (data: CreateTeamData) => Promise<void>;
    updateTeam: (teamId: string, data: Partial<CreateTeamData>) => Promise<void>;
    deleteTeam: (teamId: string) => Promise<void>;
    addTeamMember: (teamId: string, data: { user_id: string; role: string }) => Promise<void>;
}

export const useTeamStore = create<TeamState>((set, get) => ({
    // Initial state
    teams: [],
    currentTeam: null,
    isLoading: false,
    error: null,

    // Basic actions
    setCurrentTeam: (team) => set({ currentTeam: team }),
    clearError: () => set({ error: null }),

    // API actions
    fetchTeams: async (workspaceId) => {
        set({ isLoading: true, error: null });
        try {
            const teams = await TeamService.getTeams(workspaceId);
            set({ teams });

            const { currentTeam } = get();
            if (!currentTeam && teams.length > 0) {
                set({ currentTeam: teams[0] });
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch teams';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    getTeamById: async (teamId) => {
        set({ isLoading: true, error: null });
        try {
            const team = await TeamService.getTeamById(teamId);
            set(state => ({
                teams: [...state.teams.filter(t => t.id !== teamId), team],
                currentTeam: team 
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to fetch team';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    createTeam: async (data) => {
        set({ isLoading: true, error: null });
        try {
            const newTeam = await TeamService.createTeam(data);
            set(state => ({
                teams: [...state.teams, newTeam]
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to create team';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    updateTeam: async (teamId, data) => {
        set({ isLoading: true, error: null });
        try {
            const updatedTeam = await TeamService.updateTeam(teamId, data);
            set(state => ({
                teams: state.teams.map(t => t.id === teamId ? updatedTeam : t),
                currentTeam: state.currentTeam?.id === teamId ? updatedTeam : state.currentTeam
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to update team';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    deleteTeam: async (teamId) => {
        set({ isLoading: true, error: null });
        try {
            await TeamService.deleteTeam(teamId);
            set(state => ({
                teams: state.teams.filter(t => t.id !== teamId),
                currentTeam: state.currentTeam?.id === teamId ? null : state.currentTeam
            }));
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to delete team';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    addTeamMember: async (teamId, data) => {
        set({ isLoading: true, error: null });
        try {
            await TeamService.addTeamMember(teamId, data);
            // Refresh team data after adding member
            await get().getTeamById(teamId);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to add team member';
            set({ error: errorMessage });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    }
}));