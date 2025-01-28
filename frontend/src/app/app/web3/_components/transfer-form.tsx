import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { useWeb3Store } from "@/stores/web3.store";
import { LoadingState } from "../../_components/loading-state";

export function TransferForm() {
  const { transfer, validateAddress, getBalance, selectedNetwork, isLoading } =
    useWeb3Store();
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    to_address: "",
    amount: "",
    token_mint: "",
    private_key: "",
  });

  const [balance, setBalance] = useState<number | null>(null);
  const [recipientValid, setRecipientValid] = useState<boolean | null>(null);

  useEffect(() => {
    // Reset form when network changes
    setFormData({
      to_address: "",
      amount: "",
      token_mint: "",
      private_key: "",
    });
    setBalance(null);
    setRecipientValid(null);
  }, [selectedNetwork]);

  const handleAddressChange = async (address: string) => {
    setFormData((prev) => ({ ...prev, to_address: address }));
    if (address.length >= 32) {
      try {
        const isValid = await validateAddress(address);
        setRecipientValid(isValid);
      } catch {
        setRecipientValid(false);
      }
    } else {
      setRecipientValid(null);
    }
  };

  const checkBalance = async () => {
    if (formData.private_key) {
      try {
        const response = await getBalance(
          formData.private_key,
          formData.token_mint
        );
        setBalance(response.balance);
      } catch (error) {
        console.log("Error fetching balance:", error);
        toast({
          title: "Error",
          description: "Failed to fetch balance",
          variant: "destructive",
        });
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipientValid) {
      toast({
        title: "Invalid Address",
        description: "Please enter a valid recipient address",
        variant: "destructive",
      });
      return;
    }

    try {
      const taskId = await transfer({
        network: selectedNetwork,
        ...formData,
        amount: parseFloat(formData.amount),
      });

      toast({
        title: "Transfer Initiated",
        description: `Task ID: ${taskId}`,
      });

      // Reset form
      setFormData({
        to_address: "",
        amount: "",
        token_mint: "",
        private_key: "",
      });
      setBalance(null);
    } catch (error) {
      toast({
        title: "Transfer Failed",
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    }
  };

  const getAddressStyle = () => {
    if (recipientValid === null) return "";
    return recipientValid ? "border-green-500" : "border-red-500";
  };

  const insufficientFunds =
    balance !== null && parseFloat(formData.amount) > balance;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Transfer Funds</CardTitle>
        <CardDescription>Send tokens on {selectedNetwork}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="to_address">Recipient Address</Label>
            <Input
              id="to_address"
              value={formData.to_address}
              onChange={(e) => handleAddressChange(e.target.value)}
              className={getAddressStyle()}
              placeholder="Enter recipient address"
            />
            {recipientValid === false && (
              <span className="text-sm text-red-500">
                Invalid address format
              </span>
            )}
          </div>

          <div className="space-y-2">
            <Label>Token</Label>
            <Select
              value={formData.token_mint || "native_sol"}
              onValueChange={(value) => {
                setFormData((prev) => ({ ...prev, token_mint: value }));
                setBalance(null);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select token (SOL if empty)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sol">SOL</SelectItem>
                {/* Add token list here */}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <Label htmlFor="amount">Amount</Label>
              {balance !== null && (
                <span className="text-sm text-muted-foreground">
                  Balance: {balance} {formData.token_mint || "SOL"}
                </span>
              )}
            </div>
            <Input
              id="amount"
              type="number"
              step="any"
              value={formData.amount}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, amount: e.target.value }))
              }
              placeholder="Enter amount"
              className={insufficientFunds ? "border-red-500" : ""}
            />
            {insufficientFunds && (
              <span className="text-sm text-red-500">Insufficient funds</span>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <Label htmlFor="private_key">Private Key</Label>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={checkBalance}
                disabled={!formData.private_key}
              >
                Check Balance
              </Button>
            </div>
            <Input
              id="private_key"
              type="password"
              value={formData.private_key}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  private_key: e.target.value,
                }))
              }
              placeholder="Enter private key"
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={
              isLoading ||
              !formData.to_address ||
              !formData.amount ||
              !formData.private_key ||
              insufficientFunds ||
              !recipientValid
            }
          >
            {isLoading ? (
              <>
                <LoadingState message="Transferring..." />
              </>
            ) : (
              "Transfer"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
