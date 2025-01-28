import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useWeb3Store } from "@/stores/web3.store";
import { useToast } from "@/hooks/use-toast";
import { LoadingState } from "../../_components/loading-state";

export function TokenManagement() {
  const { mintTokens, burnTokens, getTokenInfo, selectedNetwork, isLoading } =
    useWeb3Store();
  const { toast } = useToast();

  const [mintData, setMintData] = useState({
    token_mint: "",
    destination: "",
    amount: "",
    private_key: "",
    mint_authority: "",
  });

  const [burnData, setBurnData] = useState({
    token_mint: "",
    source: "",
    amount: "",
    private_key: "",
  });

  const [tokenInfo, setTokenInfo] = useState<any>(null);

  useEffect(() => {
    // Reset forms when network changes
    setMintData({
      token_mint: "",
      destination: "",
      amount: "",
      private_key: "",
      mint_authority: "",
    });
    setBurnData({
      token_mint: "",
      source: "",
      amount: "",
      private_key: "",
    });
    setTokenInfo(null);
  }, [selectedNetwork]);

  const fetchTokenInfo = async (tokenMint: string) => {
    try {
      const info = await getTokenInfo(tokenMint);
      setTokenInfo(info);
    } catch (error) {
      console.error("Failed to fetch token information:", error);
      toast({
        title: "Error",
        description: "Failed to fetch token information",
        variant: "destructive",
      });
    }
  };

  const handleMint = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const taskId = await mintTokens({
        network: selectedNetwork,
        ...mintData,
        amount: parseFloat(mintData.amount),
      });

      toast({
        title: "Mint Initiated",
        description: `Task ID: ${taskId}`,
      });

      setMintData({
        token_mint: "",
        destination: "",
        amount: "",
        private_key: "",
        mint_authority: "",
      });
    } catch (error) {
      toast({
        title: "Mint Failed",
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    }
  };

  const handleBurn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const taskId = await burnTokens({
        network: selectedNetwork,
        ...burnData,
        amount: parseFloat(burnData.amount),
      });

      toast({
        title: "Burn Initiated",
        description: `Task ID: ${taskId}`,
      });

      setBurnData({
        token_mint: "",
        source: "",
        amount: "",
        private_key: "",
      });
    } catch (error) {
      toast({
        title: "Burn Failed",
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Token Management</CardTitle>
        <CardDescription>
          Mint and burn tokens on {selectedNetwork}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="mint">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="mint">Mint Tokens</TabsTrigger>
            <TabsTrigger value="burn">Burn Tokens</TabsTrigger>
          </TabsList>

          <TabsContent value="mint">
            <form onSubmit={handleMint} className="space-y-4">
              <div className="space-y-2">
                <Label>Token Mint Address</Label>
                <div className="flex gap-2">
                  <Input
                    value={mintData.token_mint}
                    onChange={(e) => {
                      setMintData((prev) => ({
                        ...prev,
                        token_mint: e.target.value,
                      }));
                      if (e.target.value) fetchTokenInfo(e.target.value);
                    }}
                    placeholder="Enter token mint address"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => fetchTokenInfo(mintData.token_mint)}
                    disabled={!mintData.token_mint}
                  >
                    Verify
                  </Button>
                </div>
                {tokenInfo && (
                  <div className="text-sm text-muted-foreground">
                    Decimals: {tokenInfo.decimals}, Supply: {tokenInfo.supply}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Destination Address</Label>
                <Input
                  value={mintData.destination}
                  onChange={(e) =>
                    setMintData((prev) => ({
                      ...prev,
                      destination: e.target.value,
                    }))
                  }
                  placeholder="Enter destination address"
                />
              </div>

              <div className="space-y-2">
                <Label>Amount</Label>
                <Input
                  type="number"
                  step="any"
                  value={mintData.amount}
                  onChange={(e) =>
                    setMintData((prev) => ({ ...prev, amount: e.target.value }))
                  }
                  placeholder="Enter amount"
                />
              </div>

              <div className="space-y-2">
                <Label>Mint Authority (Optional)</Label>
                <Input
                  value={mintData.mint_authority}
                  onChange={(e) =>
                    setMintData((prev) => ({
                      ...prev,
                      mint_authority: e.target.value,
                    }))
                  }
                  placeholder="Enter mint authority"
                />
              </div>

              <div className="space-y-2">
                <Label>Private Key</Label>
                <Input
                  type="password"
                  value={mintData.private_key}
                  onChange={(e) =>
                    setMintData((prev) => ({
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
                  !mintData.token_mint ||
                  !mintData.destination ||
                  !mintData.amount ||
                  !mintData.private_key
                }
              >
                {isLoading ? (
                  <>
                    <LoadingState message="Minting..." />
                  </>
                ) : (
                  "Mint Tokens"
                )}
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="burn">
            <form onSubmit={handleBurn} className="space-y-4">
              <div className="space-y-2">
                <Label>Token Mint Address</Label>
                <div className="flex gap-2">
                  <Input
                    value={burnData.token_mint}
                    onChange={(e) => {
                      setBurnData((prev) => ({
                        ...prev,
                        token_mint: e.target.value,
                      }));
                      if (e.target.value) fetchTokenInfo(e.target.value);
                    }}
                    placeholder="Enter token mint address"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => fetchTokenInfo(burnData.token_mint)}
                    disabled={!burnData.token_mint}
                  >
                    Verify
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Source Address</Label>
                <Input
                  value={burnData.source}
                  onChange={(e) =>
                    setBurnData((prev) => ({ ...prev, source: e.target.value }))
                  }
                  placeholder="Enter source address"
                />
              </div>

              <div className="space-y-2">
                <Label>Amount</Label>
                <Input
                  type="number"
                  step="any"
                  value={burnData.amount}
                  onChange={(e) =>
                    setBurnData((prev) => ({ ...prev, amount: e.target.value }))
                  }
                  placeholder="Enter amount"
                />
              </div>

              <div className="space-y-2">
                <Label>Private Key</Label>
                <Input
                  type="password"
                  value={burnData.private_key}
                  onChange={(e) =>
                    setBurnData((prev) => ({
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
                  !burnData.token_mint ||
                  !burnData.source ||
                  !burnData.amount ||
                  !burnData.private_key
                }
              >
                {isLoading ? (
                  <>
                    <LoadingState message="Burning..." />
                  </>
                ) : (
                  "Burn Tokens"
                )}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
