import axiosInstance from "@/lib/axios/axios-instance";
import { 
    Web3Network, 
    TransferRequest, 
    MintRequest, 
    BurnRequest,
    StakeRequest,
    UnstakeRequest,
    Web3Response,
    TokenInfo,
    ValidatorInfo,
    Web3Task
} from "@/types/web3.types";
import axios from "axios";

const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || '';

export class Web3Service {
    static async transfer(data: TransferRequest): Promise<Web3Response> {
        try {
            const response = await axiosInstance.post(
                `${FASTAPI_BASE_URL}/web3/transfer`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Transfer failed');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getBalance(address: string, token_mint?: string): Promise<{ balance: number; decimals: number; token: string }> {
        try {
            const response = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/web3/balance/${address}`,
                { params: { token_mint } }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch balance');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getTokenInfo(token_mint: string): Promise<TokenInfo> {
        try {
            const response = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/web3/token/${token_mint}`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch token info');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async mintTokens(data: MintRequest): Promise<Web3Response> {
        try {
            const response = await axiosInstance.post(
                `${FASTAPI_BASE_URL}/web3/mint`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Minting failed');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async burnTokens(data: BurnRequest): Promise<Web3Response> {
        try {
            const response = await axiosInstance.post(
                `${FASTAPI_BASE_URL}/web3/burn`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Burning failed');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async stakeSol(data: StakeRequest): Promise<Web3Response> {
        try {
            const response = await axiosInstance.post(
                `${FASTAPI_BASE_URL}/web3/stake`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Staking failed');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async unstakeSol(data: UnstakeRequest): Promise<Web3Response> {
        try {
            const response = await axiosInstance.post(
                `${FASTAPI_BASE_URL}/web3/unstake`,
                data
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Unstaking failed');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getStakeInfo(network: Web3Network, stake_account: string): Promise<any> {
        try {
            const response = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/web3/stake/${stake_account}`,
                { params: { network } }
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch stake info');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async validateAddress(address: string): Promise<boolean> {
        try {
            const response = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/web3/validate/${address}`
            );
            return response.data.valid;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Address validation failed');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getValidators(network: Web3Network): Promise<ValidatorInfo[]> {
        try {
            const response = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/web3/validators/${network}`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch validators');
            }
            throw new Error('An unexpected error occurred');
        }
    }

    static async getTaskStatus(taskId: string): Promise<Web3Task> {
        try {
            const response = await axiosInstance.get(
                `${FASTAPI_BASE_URL}/web3/task/${taskId}`
            );
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(error.response?.data?.detail || 'Failed to fetch task status');
            }
            throw new Error('An unexpected error occurred');
        }
    }
}