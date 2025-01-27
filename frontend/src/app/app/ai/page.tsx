"use client";

import { useEffect, useState } from "react";
import { AITask, AIModelType } from "@/types/ai.types";

import { ModelsPanel } from "./_components/models-panel";
import { TaskFilters } from "./_components/task-filters";

import { BatchProcessModal } from "./_components/modals/batch-process";
import { useTaskPolling } from "@/hooks/useTaskPolling";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAIStore } from "@/stores/ai.store";
import { PageHeader } from "../_components/page-header";
import { AIHeader } from "./_components/ai-header";
import { AIStatsCards } from "./_components/ai-stats-card";
import { TaskTable } from "./_components/task-table";
import { TaskDetailsPanel } from "./_components/task-detail-panel";
import { CreateTaskModal } from "./_components/modals/create-task";

export default function AIPage() {
  // State
  const [selectedTask, setSelectedTask] = useState<AITask | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("tasks");
  const [statusFilter, setStatusFilter] = useState("all");
  const [modelFilter, setModelFilter] = useState<AIModelType | null>(null);
  const [sortKey, setSortKey] = useState("created_desc");

  // Hooks
  const { toast } = useToast();
  const { tasks, models, isLoading, error, listTasks, getModels } =
    useAIStore();

  useTaskPolling(selectedTask?.workflow_id);

  // Effects
  useEffect(() => {
    const init = async () => {
      try {
        await Promise.all([listTasks(), getModels()]);
      } catch (error) {
        console.log("Error loading initial data:", error);
        toast({
          title: "Error",
          description: "Failed to load initial data",
          variant: "destructive",
        });
      }
    };
    init();
  }, []);

  // Handlers
  const handleRefresh = async () => {
    try {
      if (activeTab === "tasks") {
        await listTasks();
      } else {
        await getModels();
      }
    } catch (error) {
      console.log("Error refreshing data:", error);
      toast({
        title: "Error",
        description: "Failed to refresh data",
        variant: "destructive",
      });
    }
  };

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h3 className="text-lg font-semibold">Something went wrong</h3>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col space-y-6">
      <PageHeader
        heading="AI Processing"
        text="Manage and monitor your AI processing tasks"
      />

      <div className="flex h-full flex-col">
        <AIHeader
          onSearch={setSearchQuery}
          onCreateNew={() => setIsCreateModalOpen(true)}
          onBatchProcess={() => setIsBatchModalOpen(true)}
          onRefresh={handleRefresh}
        />

        <AIStatsCards />

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
          <TabsList className="px-4">
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="models">Models</TabsTrigger>
          </TabsList>

          <TabsContent value="tasks" className="flex-1">
            <div className="p-4">
              <TaskFilters
                onStatusFilter={setStatusFilter}
                onModelFilter={setModelFilter}
                onSort={setSortKey}
              />
              {isLoading ? (
                <div className="flex h-[400px] items-center justify-center">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <TaskTable
                  tasks={tasks}
                  searchQuery={searchQuery}
                  statusFilter={statusFilter}
                  modelFilter={modelFilter}
                  sortKey={sortKey}
                  onSelect={setSelectedTask}
                />
              )}
            </div>
          </TabsContent>

          <TabsContent value="models">
            {isLoading ? (
              <div className="flex h-[400px] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin" />
              </div>
            ) : (
              <ModelsPanel models={models} />
            )}
          </TabsContent>
        </Tabs>

        {selectedTask && (
          <TaskDetailsPanel
            task={selectedTask}
            onClose={() => setSelectedTask(null)}
          />
        )}

        <CreateTaskModal
          open={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
        />

        <BatchProcessModal
          open={isBatchModalOpen}
          onClose={() => setIsBatchModalOpen(false)}
        />
      </div>
    </div>
  );
}
