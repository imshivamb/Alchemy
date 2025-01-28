export enum Web3Network {
    MAINNET = "solana-mainnet",
    TESTNET = "solana-testnet",
    DEVNET = "solana-devnet"
}

export enum Web3ActionType {
    TRANSFER = "transfer",
    MINT = "mint",
    BURN = "burn",
    STAKE = "stake",
    UNSTAKE = "unstake"
}

export enum TransactionStatus {
    PENDING = "pending",
    PROCESSING = "processing",
    COMPLETED = "completed",
    FAILED = "failed"
}

export interface TransferRequest {
    network: Web3Network;
    to_address: string;
    amount: number;
    token_mint?: string;
    private_key: string;
}

export interface MintRequest {
    network: Web3Network;
    token_mint: string;
    destination: string;
    amount: number;
    private_key: string;
    mint_authority?: string;
}

export interface BurnRequest {
    network: Web3Network;
    token_mint: string;
    amount: number;
    source: string;
    private_key: string;
    mint_authority?: string;
}

export interface StakeRequest {
    network: Web3Network;
    validator: string;
    amount: number;
    private_key: string;
}

export interface UnstakeRequest {
    network: Web3Network;
    stake_account: string;
    private_key: string;
}

export interface Web3Response {
    task_id: string;
    status: string;
    message: string;
}

export interface TokenConfig {
    mint: string;
    decimals: number;
}

export interface GasConfig {
    priority_fee?: number;
    max_fee?: number;
}

export interface Web3Config {
    network: Web3Network;
    action_type: Web3ActionType;
    amount?: string;
    recipient?: string;
    token?: TokenConfig;
    contract_address?: string;
    function_name?: string;
    parameters?: Record<string, any>;
    gas_config?: GasConfig;
}

export interface Web3Task {
    workflow_id: string;
    action_type: Web3ActionType;
    network: Web3Network;
    params: Record<string, any>;
    user_id: string;
    status: TransactionStatus;
    created_at: string;
    result: any;
    error?: string;
}

export interface TokenInfo {
    decimals: number;
    supply: number;
    freeze_authority?: string;
    mint_authority?: string;
}

export interface ValidatorInfo {
    pubkey: string;
    node_pubkey: string;
    activated_stake: number;
    commission: number;
    last_vote: number;
    root_slot: number;
    credits: number;
    epoch_vote_account: boolean;
}