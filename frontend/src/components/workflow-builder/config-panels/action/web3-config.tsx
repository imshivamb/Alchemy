import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Web3ActionType,
  Web3Config as Web3ConfigType,
  Web3Network,
} from "@/types/workflow.types";
import React from "react";

interface Web3ConfigProps {
  config: Web3ConfigType;
  onChange: (config: Web3ConfigType) => void;
}

export const Web3Config: React.FC<Web3ConfigProps> = ({ config, onChange }) => {
  return (
    <div className="space-y-4">
      <Select
        value={config?.network ?? "solana-mainnet"}
        onValueChange={(value: Web3Network) =>
          onChange({ ...config, network: value })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Select network" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="solana-mainnet">Solana Mainnet</SelectItem>
          <SelectItem value="solana-devnet">Solana Devnet</SelectItem>
          <SelectItem value="solana-testnet">Solana Testnet</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={config?.actionType ?? "transfer"}
        onValueChange={(value: Web3ActionType) =>
          onChange({ ...config, actionType: value })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Select action" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="transfer">Transfer</SelectItem>
          <SelectItem value="mint">Mint</SelectItem>
          <SelectItem value="burn">Burn</SelectItem>
          <SelectItem value="stake">Stake</SelectItem>
          <SelectItem value="unstake">Unstake</SelectItem>
        </SelectContent>
      </Select>

      <Input
        placeholder="Wallet address"
        value={config?.wallet ?? ""}
        onChange={(e) => onChange({ ...config, wallet: e.target.value })}
      />

      {(config?.actionType === "transfer" || config?.actionType === "mint") && (
        <Input
          placeholder="Recipient address"
          value={config?.recipient ?? ""}
          onChange={(e) => onChange({ ...config, recipient: e.target.value })}
        />
      )}

      <Input
        placeholder="Amount"
        type="number"
        value={config?.amount ?? ""}
        onChange={(e) => onChange({ ...config, amount: e.target.value })}
      />

      {/* Token configuration */}
      <div className="space-y-2">
        <Label>Token Configuration</Label>
        <Input
          placeholder="Token mint address"
          value={config?.token?.mint ?? ""}
          onChange={(e) =>
            onChange({
              ...config,
              token: {
                ...config.token,
                mint: e.target.value,
              },
            })
          }
        />
        <Input
          placeholder="Decimals"
          type="number"
          value={config?.token?.decimals ?? ""}
          onChange={(e) =>
            onChange({
              ...config,
              token: {
                ...config.token,
                decimals: parseInt(e.target.value),
              },
            })
          }
        />
      </div>

      {/* Gas configuration */}
      <div className="space-y-2">
        <Label>Gas Configuration</Label>
        <Input
          placeholder="Priority fee"
          type="number"
          value={config?.gasConfig?.priorityFee ?? ""}
          onChange={(e) =>
            onChange({
              ...config,
              gasConfig: {
                ...config.gasConfig,
                priorityFee: parseFloat(e.target.value),
              },
            })
          }
        />
        <Input
          placeholder="Max fee"
          type="number"
          value={config?.gasConfig?.maxFee ?? ""}
          onChange={(e) =>
            onChange({
              ...config,
              gasConfig: {
                ...config.gasConfig,
                maxFee: parseFloat(e.target.value),
              },
            })
          }
        />
      </div>
    </div>
  );
};
