import { Web3Network } from "@/types/web3.types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface NetworkSelectorProps {
  selected: Web3Network;
  onSelect: (network: Web3Network) => void;
}

export function NetworkSelector({ selected, onSelect }: NetworkSelectorProps) {
  return (
    <div className="flex items-center justify-between p-4 border-b">
      <span className="text-sm font-medium">Network</span>
      <Select
        value={selected}
        onValueChange={(value) => onSelect(value as Web3Network)}
      >
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Select network" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={Web3Network.MAINNET}>Mainnet</SelectItem>
          <SelectItem value={Web3Network.TESTNET}>Testnet</SelectItem>
          <SelectItem value={Web3Network.DEVNET}>Devnet</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
