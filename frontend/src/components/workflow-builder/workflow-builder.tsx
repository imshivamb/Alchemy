// components/workflow-builder/WorkflowBuilder.tsx

import React, { useCallback } from "react";
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  Panel,
} from "reactflow";
import { useWorkflowState } from "@/stores/workflow.store";
import NodePalette from "./sidebar/node-palette";
import { ConfigPanel } from "./sidebar/config-panel";
import TriggerNode from "./nodes/trigger-node";
import ActionNode from "./nodes/action-node";
import ConditionNode from "./nodes/condition-node";
import { Button } from "@/components/ui/button";
import { Save, Play } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import "reactflow/dist/style.css";

const nodeTypes = {
  trigger: TriggerNode,
  action: ActionNode,
  condition: ConditionNode,
};

export const WorkflowBuilder: React.FC = () => {
  const {
    nodes,
    edges,
    onEdgesChange,
    onNodeChange,
    onConnect,
    selectedNode,
    setSelectedNode,
    isValid,
    validationErrors,
    isDirty,
    validateWorkflow,
  } = useWorkflowState();

  const handleSave = useCallback(async () => {
    if (!validateWorkflow()) {
      return;
    }
    // Save functionality will be implemented when we create the API
  }, [validateWorkflow]);

  const handleExecute = useCallback(async () => {
    if (!validateWorkflow()) {
      return;
    }
    // Execute functionality will be implemented when we create the API
  }, [validateWorkflow]);

  return (
    <div className="flex h-screen">
      {/* Node Palette */}
      <div className="w-64 border-r bg-background">
        <NodePalette />
      </div>

      {/* Flow Canvas */}
      <div className="flex-1 flex flex-col">
        <div className="h-12 border-b flex items-center justify-between px-4 bg-background">
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              onClick={handleSave}
              disabled={!isDirty || !isValid}
            >
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={handleExecute}
              disabled={!isValid}
            >
              <Play className="h-4 w-4 mr-2" />
              Execute
            </Button>
          </div>
        </div>

        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodeChange={onNodeChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(_, node) => setSelectedNode(node)}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background variant={BackgroundVariant.Dots} />
            <Controls />
            <MiniMap />

            {/* Validation Errors */}
            {!isValid && (
              <Panel position="bottom-center" className="mb-8">
                <Alert variant="destructive">
                  <AlertDescription>{validationErrors[0]}</AlertDescription>
                </Alert>
              </Panel>
            )}
          </ReactFlow>
        </div>
      </div>

      {/* Configuration Panel */}
      <div className="w-96 border-l bg-background">
        <ConfigPanel selectedNode={selectedNode} />
      </div>
    </div>
  );
};

export default WorkflowBuilder;
