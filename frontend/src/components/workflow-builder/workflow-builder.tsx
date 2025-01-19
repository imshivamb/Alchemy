"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  Controls,
  NodeTypes,
  Node,
  NodeProps,
} from "@xyflow/react";
import { useWorkflowStore } from "@/stores/workflow.store";
import TriggerNode from "./nodes/trigger-node";
import ActionNode from "./nodes/action-node";
import ConditionNode from "./nodes/condition-node";
import { WorkflowNode } from "@/types/workflow.types";
import "reactflow/dist/style.css";
import { AccountConnectionModal } from "./_components/account-connection-modal";
import { TriggerSelectionModal } from "./_components/trigger-selection-modal";
import { AppSelectionModal } from "./_components/app-selection-modal";
import { ConfigurationPanel } from "./sidebar/config-panel";
import { WorkflowHeader } from "./_components/workflow-header";
import { WorkflowSidebar } from "./_components/workflow-sidebar";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import { toast } from "sonner";
import { useParams } from "next/navigation";

export const WorkflowBuilder: React.FC = () => {
  const [modalState, setModalState] = useState<{
    type:
      | "app-select"
      | "trigger-select"
      | "account-connect"
      | "rename"
      | "note"
      | null;
    selectedApp?: string;
    nodeId?: string;
  }>({ type: null });
  const {
    nodes,
    edges,
    onEdgesChange,
    onNodeChange,
    onConnect,
    selectedNode,
    setSelectedNode,
    isValid,
    isDirty,
    validateWorkflow,
    updateNode,
    setNodes,
    addNode,
  } = useWorkflowStore();
  const { currentWorkflow, updateWorkflow, getWorkflowById } =
    useWorkflowApiStore();
  const [workflowName, setWorkflowName] = useState("Untitled workflow");
  const [selectedSidePanel, setSelectedSidePanel] = useState<string | null>(
    null
  );
  const params = useParams();

  useEffect(() => {
    const workflowId = params?.id as string;
    if (workflowId && !currentWorkflow) {
      getWorkflowById(Number(workflowId));
    }
  }, [params?.id, currentWorkflow, getWorkflowById]);

  const handleWorkflowNameChange = async (name: string) => {
    setWorkflowName(name);
    if (currentWorkflow) {
      try {
        await updateWorkflow(currentWorkflow.id, { name: name });
      } catch (error) {
        toast.error("Failed to update workflow name");
        console.log("Error updating workflow name:", error);
      }
    }
  };

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (node.type === "trigger" && !node.data.appId) {
        setModalState({ type: "app-select" });
      }
      setSelectedNode(node as unknown as WorkflowNode);
    },
    [setSelectedNode]
  );
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

  const handleNodeAction = useCallback(
    (action: "rename" | "copy" | "note", nodeId: string) => {
      switch (action) {
        case "rename":
          setModalState({ type: "rename", nodeId });
          break;
        case "copy":
          const nodeToCopy = nodes.find((n) => n.id === nodeId);
          if (nodeToCopy) {
            const newNode = {
              ...nodeToCopy,
              id: `${nodeToCopy.type}-${Date.now()}`,
              position: {
                x: nodeToCopy.position.x + 50,
                y: nodeToCopy.position.y + 50,
              },
            };
            addNode(newNode);
          }
          break;
        case "note":
          setModalState({ type: "note", nodeId });
          break;
      }
    },
    [nodes, addNode]
  );

  // Create wrapper components to handle the ReactFlow node props
  const TriggerNodeWrapper = (props: NodeProps) => (
    <TriggerNode
      {...(props as any)}
      isValidConnection={() => true}
      onAction={(action: "rename" | "copy" | "note") =>
        handleNodeAction(action, props.id)
      } // Add type here
    />
  );

  const ActionNodeWrapper = (props: NodeProps) => (
    <ActionNode
      {...(props as any)}
      isValidConnection={() => true}
      onAction={(action: "rename" | "copy" | "note") =>
        handleNodeAction(action, props.id)
      } // Add type here
    />
  );

  const ConditionNodeWrapper = (props: NodeProps) => (
    <ConditionNode {...(props as any)} isValidConnection={() => true} />
  );

  const nodeTypes: NodeTypes = {
    trigger: TriggerNodeWrapper,
    action: ActionNodeWrapper,
    condition: ConditionNodeWrapper,
  };

  useEffect(() => {
    if (nodes.length === 0) {
      const initialNode = {
        id: "trigger-1",
        type: "trigger",
        position: { x: window.innerWidth / 3, y: 100 },
        data: {
          label: "Choose a trigger app",
          description: "Click to start configuring your workflow",
          isValid: false,
          isConfigured: false,
          config: {},
          outputSchema: {
            type: "object",
            properties: {},
          },
        },
      };

      setNodes([initialNode]);
    }
  }, [nodes.length]);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Canvas */}
      <WorkflowSidebar
        selectedPanel={selectedSidePanel}
        onPanelChange={setSelectedSidePanel}
      />
      <div className="flex-1 flex flex-col">
        <WorkflowHeader
          workflowName={workflowName}
          setWorkflowName={handleWorkflowNameChange}
          onSave={handleSave}
          onTest={handleExecute}
          isValid={isValid}
          isDirty={isDirty}
        />

        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodeChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={handleNodeClick}
            nodeTypes={nodeTypes}
            zoomOnScroll={false}
            panOnScroll={true}
            fitView
          >
            <Background variant={BackgroundVariant.Dots} />
            <Controls />
          </ReactFlow>
        </div>
      </div>

      {/* Modals */}
      <AppSelectionModal
        isOpen={modalState.type === "app-select"}
        onClose={() => setModalState({ type: null })}
        onSelectApp={(appId) => {
          setModalState({ type: "trigger-select", selectedApp: appId });
        }}
      />

      <TriggerSelectionModal
        isOpen={modalState.type === "trigger-select"}
        onClose={() => setModalState({ type: "app-select" })}
        selectedAppId={modalState.selectedApp!}
        onSelectTrigger={(triggerId) => {
          setModalState({
            type: "account-connect",
            selectedApp: modalState.selectedApp,
          });
          // Update the trigger node with the selected app and trigger
          if (selectedNode) {
            updateNode(selectedNode.id, {
              appId: modalState.selectedApp,
              triggerId,
              isConfigured: false,
            });
          }
        }}
      />

      <AccountConnectionModal
        isOpen={modalState.type === "account-connect"}
        onClose={() => setModalState({ type: null })}
        appId={modalState.selectedApp!}
        onConnect={() => {
          setModalState({ type: null });
          if (selectedNode) {
            updateNode(selectedNode.id, {
              isConfigured: true,
            });
          }
        }}
      />

      {/* Configuration Panel */}
      {selectedNode &&
        (selectedNode.type === "trigger" || selectedNode.type === "action") &&
        selectedNode.data.isConfigured && (
          <div className="w-96 border-l bg-background">
            <ConfigurationPanel node={selectedNode} onUpdate={updateNode} />
          </div>
        )}
    </div>
  );
};

export default WorkflowBuilder;
