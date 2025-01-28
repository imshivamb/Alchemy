"use client";

import { useEffect, useState } from "react";
import { Web3Task } from "@/types/web3.types";
import { TransferForm } from "./_components/transfer-form";
import { TokenManagement } from "./_components/token-management";
import { StakingDashboard } from "./_components/staking-dashboard";
import { TaskMonitor } from "./_components/task-monitor";
import { TransactionHistory } from "./_components/transaction-history";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useWeb3Store } from "@/stores/web3.store";
import { LoadingState } from "../_components/loading-state";
import { ErrorState } from "../_components/error-state";
import { PageHeader } from "../_components/page-header";
import { NetworkSelector } from "./_components/network-selector";
import { TaskDetailsPanel } from "./_components/task-details-panel";

export default function Web3Page() {
  const [selectedTask, setSelectedTask] = useState<Web3Task | null>(null);
  const [activeTab, setActiveTab] = useState("transfer");
  const {
    selectedNetwork,
    setSelectedNetwork,
    isLoading,
    error,
    clearError,
    getValidators,
  } = useWeb3Store();

  useEffect(() => {
    if (activeTab === "staking") {
      getValidators(selectedNetwork).catch(console.warn);
    }
  }, [activeTab, selectedNetwork]);

  if (isLoading) {
    return <LoadingState message="Loading Web3 operations..." />;
  }

  if (error) {
    return (
      <ErrorState
        message={error}
        onRetry={() => {
          clearError();
          if (selectedNetwork) {
            getValidators(selectedNetwork);
          }
        }}
      />
    );
  }

  return (
    <div className="flex h-full flex-col space-y-6">
      <PageHeader
        heading="Web3 Operations"
        text="Manage transfers, tokens, and staking operations"
      />

      <div className="flex h-full flex-col">
        <NetworkSelector
          selected={selectedNetwork}
          onSelect={setSelectedNetwork}
        />

        <Tabs defaultValue="transfer" className="flex-1">
          <TabsList className="w-full justify-start border-b px-6">
            <TabsTrigger value="transfer">Transfer</TabsTrigger>
            <TabsTrigger value="tokens">Tokens</TabsTrigger>
            <TabsTrigger value="staking">Staking</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
          </TabsList>

          <div className="p-6">
            <TabsContent value="transfer" className="m-0">
              <div className="grid grid-cols-12 gap-6">
                <div className="col-span-5">
                  <TransferForm />
                </div>
                <div className="col-span-7">
                  <TransactionHistory />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="tokens" className="m-0">
              <TokenManagement />
            </TabsContent>

            <TabsContent value="staking" className="m-0">
              <StakingDashboard />
            </TabsContent>

            <TabsContent value="tasks" className="m-0">
              <TaskMonitor onSelectTask={setSelectedTask} />
            </TabsContent>
          </div>
        </Tabs>

        {selectedTask && (
          <TaskDetailsPanel
            task={selectedTask}
            onClose={() => setSelectedTask(null)}
          />
        )}
      </div>
    </div>
  );
}
