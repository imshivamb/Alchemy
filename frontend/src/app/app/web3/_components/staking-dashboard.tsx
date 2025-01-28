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
import { useToast } from "@/hooks/use-toast";
import { useWeb3Store } from "@/stores/web3.store";
import { LoadingState } from "../../_components/loading-state";
import { ValidatorList } from "./validator-list";

export function StakingDashboard() {
  const { stakeSol, unstakeSol, getValidators, selectedNetwork, isLoading } =
    useWeb3Store();
  const [isLoadingValidators, setIsLoadingValidators] = useState(false);
  const { toast } = useToast();

  const [stakeData, setStakeData] = useState({
    amount: "",
    validator: "",
    private_key: "",
  });

  const [unstakeData, setUnstakeData] = useState({
    stake_account: "",
    private_key: "",
  });

  useEffect(() => {
    const loadValidators = async () => {
      setIsLoadingValidators(true);
      try {
        await getValidators(selectedNetwork);
      } catch (error) {
        console.warn("Failed to load validators:", error);
        // Don't show error state, just show empty validator list
      } finally {
        setIsLoadingValidators(false);
      }
    };

    loadValidators();
  }, [selectedNetwork]);

  const handleStake = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const taskId = await stakeSol({
        network: selectedNetwork,
        ...stakeData,
        amount: parseFloat(stakeData.amount),
      });

      toast({
        title: "Stake Initiated",
        description: `Task ID: ${taskId}`,
      });

      setStakeData({
        amount: "",
        validator: "",
        private_key: "",
      });
    } catch (error) {
      toast({
        title: "Staking Failed",
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    }
  };

  const handleUnstake = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const taskId = await unstakeSol({
        network: selectedNetwork,
        ...unstakeData,
      });

      toast({
        title: "Unstake Initiated",
        description: `Task ID: ${taskId}`,
      });

      setUnstakeData({
        stake_account: "",
        private_key: "",
      });
    } catch (error) {
      toast({
        title: "Unstaking Failed",
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="grid grid-cols-12 gap-4">
      <div className="col-span-4 space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Stake SOL</CardTitle>
            <CardDescription>Stake your SOL to earn rewards</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleStake} className="space-y-4">
              <div className="space-y-2">
                <Label>Amount (SOL)</Label>
                <Input
                  type="number"
                  step="any"
                  value={stakeData.amount}
                  onChange={(e) =>
                    setStakeData((prev) => ({
                      ...prev,
                      amount: e.target.value,
                    }))
                  }
                  placeholder="Enter amount to stake"
                />
              </div>

              <div className="space-y-2">
                <Label>Private Key</Label>
                <Input
                  type="password"
                  value={stakeData.private_key}
                  onChange={(e) =>
                    setStakeData((prev) => ({
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
                  !stakeData.amount ||
                  !stakeData.validator ||
                  !stakeData.private_key
                }
              >
                {isLoading ? (
                  <LoadingState message="Staking..." />
                ) : (
                  "Stake SOL"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Unstake SOL</CardTitle>
            <CardDescription>Withdraw your staked SOL</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUnstake} className="space-y-4">
              <div className="space-y-2">
                <Label>Stake Account</Label>
                <Input
                  value={unstakeData.stake_account}
                  onChange={(e) =>
                    setUnstakeData((prev) => ({
                      ...prev,
                      stake_account: e.target.value,
                    }))
                  }
                  placeholder="Enter stake account address"
                />
              </div>

              <div className="space-y-2">
                <Label>Private Key</Label>
                <Input
                  type="password"
                  value={unstakeData.private_key}
                  onChange={(e) =>
                    setUnstakeData((prev) => ({
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
                  !unstakeData.stake_account ||
                  !unstakeData.private_key
                }
              >
                {isLoading ? (
                  <>
                    <LoadingState message="Unstaking..." />
                  </>
                ) : (
                  "Unstake SOL"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <div className="col-span-8">
        {isLoadingValidators ? (
          <LoadingState message="Loading validators..." />
        ) : (
          <ValidatorList
            onSelectValidator={(validator) =>
              setStakeData((prev) => ({ ...prev, validator }))
            }
          />
        )}
      </div>
    </div>
  );
}
