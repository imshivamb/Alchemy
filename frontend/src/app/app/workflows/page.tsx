"use client";

import { Sheet, SheetContent } from "@/components/ui/sheet";

import { useEffect, useState } from "react";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import { Workflow } from "@/types/workflow-api.types";
import { WorkflowHeader } from "./_components/workflow-header";
import { WorkflowGrid } from "./_components/workflow-grid";
import { WorkflowDetailsPanel } from "./_components/workflow-details";
import { CreateWorkflowModal } from "./_components/modals/create-workflow";

export default function WorkflowsPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(
    null
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { workflows, fetchWorkflows, fetchWorkflowLimits } =
    useWorkflowApiStore();

  useEffect(() => {
    fetchWorkflows();
    fetchWorkflowLimits();
  }, [fetchWorkflows, fetchWorkflowLimits]);

  return (
    <div className="flex h-screen bg-background">
      <div className="flex-1 flex flex-col">
        <WorkflowHeader
          onSearch={setSearchQuery}
          onCreateNew={() => setShowCreateModal(true)}
        />

        <div className="flex-1 p-6">
          <WorkflowGrid
            workflows={workflows}
            searchQuery={searchQuery}
            onSelect={setSelectedWorkflow}
          />
        </div>
      </div>

      <Sheet
        open={!!selectedWorkflow}
        onOpenChange={() => setSelectedWorkflow(null)}
      >
        <SheetContent className="w-[600px] sm:w-[600px]">
          {selectedWorkflow && (
            <WorkflowDetailsPanel
              workflow={selectedWorkflow}
              onClose={() => setSelectedWorkflow(null)}
            />
          )}
        </SheetContent>
      </Sheet>

      <CreateWorkflowModal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
}
