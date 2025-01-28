import { create } from 'zustand';
import { Web3Service } from '@/services/web3-service';
import { 
   Web3Network,
   Web3Task,
   TokenInfo,
   ValidatorInfo,
   TransferRequest,
   MintRequest,
   BurnRequest,
   StakeRequest,
   UnstakeRequest
} from '@/types/web3.types';

interface Web3State {
   // State
   tasks: Web3Task[];
   currentTask: Web3Task | null;
   validators: ValidatorInfo[];
   selectedNetwork: Web3Network;
   isLoading: boolean;
   error: string | null;

   // Basic actions
   setCurrentTask: (task: Web3Task | null) => void;
   setSelectedNetwork: (network: Web3Network) => void;
   clearError: () => void;

   // Service actions
   transfer: (data: TransferRequest) => Promise<string>;
   mintTokens: (data: MintRequest) => Promise<string>;
   burnTokens: (data: BurnRequest) => Promise<string>;
   stakeSol: (data: StakeRequest) => Promise<string>;
   unstakeSol: (data: UnstakeRequest) => Promise<string>;
   getBalance: (address: string, token_mint?: string) => Promise<{ balance: number; decimals: number; token: string }>;
   getTokenInfo: (token_mint: string) => Promise<TokenInfo>;
   getValidators: (network: Web3Network) => Promise<void>;
   validateAddress: (address: string) => Promise<boolean>;
   getTaskStatus: (taskId: string) => Promise<void>;
}

export const useWeb3Store = create<Web3State>((set) => ({
   tasks: [],
   currentTask: null,
   validators: [],
   selectedNetwork: Web3Network.DEVNET,
   isLoading: false,
   error: null,

   setCurrentTask: (task) => set({ currentTask: task }),
   setSelectedNetwork: (network) => set({ selectedNetwork: network }),
   clearError: () => set({ error: null }),

   transfer: async (data) => {
       set({ isLoading: true, error: null });
       try {
           const response = await Web3Service.transfer(data);
           return response.task_id;
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Transfer failed';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   mintTokens: async (data) => {
       set({ isLoading: true, error: null });
       try {
           const response = await Web3Service.mintTokens(data);
           return response.task_id;
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Minting failed';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   burnTokens: async (data) => {
       set({ isLoading: true, error: null });
       try {
           const response = await Web3Service.burnTokens(data);
           return response.task_id;
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Burning failed';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   stakeSol: async (data) => {
       set({ isLoading: true, error: null });
       try {
           const response = await Web3Service.stakeSol(data);
           return response.task_id;
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Staking failed';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   unstakeSol: async (data) => {
       set({ isLoading: true, error: null });
       try {
           const response = await Web3Service.unstakeSol(data);
           return response.task_id;
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Unstaking failed';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getBalance: async (address, token_mint) => {
       set({ isLoading: true, error: null });
       try {
           return await Web3Service.getBalance(address, token_mint);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to fetch balance';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getTokenInfo: async (token_mint) => {
       set({ isLoading: true, error: null });
       try {
           return await Web3Service.getTokenInfo(token_mint);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to fetch token info';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getValidators: async (network) => {
       set({ isLoading: true, error: null });
       try {
           const validators = await Web3Service.getValidators(network);
           set({ validators });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to fetch validators';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   validateAddress: async (address) => {
       set({ isLoading: true, error: null });
       try {
           return await Web3Service.validateAddress(address);
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Address validation failed';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   },

   getTaskStatus: async (taskId) => {
       set({ isLoading: true, error: null });
       try {
           const task = await Web3Service.getTaskStatus(taskId);
           set({ currentTask: task });
       } catch (error) {
           const errorMessage = error instanceof Error ? error.message : 'Failed to fetch task status';
           set({ error: errorMessage });
           throw error;
       } finally {
           set({ isLoading: false });
       }
   }
}));