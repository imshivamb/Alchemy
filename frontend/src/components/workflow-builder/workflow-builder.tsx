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
import { NodeAction, WorkflowNode } from "@/types/workflow.types";
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
import { WebhookGenerationModal } from "./_components/modals/webhook-gen-modal";

type ModalState = {
  type:
    | "app-select"
    | "trigger-select"
    | "account-connect"
    | "webhook-generate"
    | "rename"
    | "note"
    | null;
  selectedApp?: string;
  nodeId?: string;
};

export const WorkflowBuilder: React.FC = () => {
  const [modalState, setModalState] = useState<ModalState>({ type: null });
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
    configureNode,
  } = useWorkflowStore();
  const { currentWorkflow, updateWorkflow, getWorkflowById } =
    useWorkflowApiStore();
  const [workflowName, setWorkflowName] = useState("Untitled workflow");
  const [selectedSidePanel, setSelectedSidePanel] = useState<string | null>(
    null
  );
  const [isSaving, setIsSaving] = useState(false);
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
        console.error(error);
        toast.error("Failed to update workflow name");
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

  const handleTriggerSelection = (triggerId: string) => {
    if (!selectedNode) return;

    const isWebhook =
      modalState.selectedApp === "webhook" && triggerId === "incoming_webhook";

    if (isWebhook) {
      configureNode(selectedNode.id, {
        appId: modalState.selectedApp,
        triggerId,
        isConfigured: false,
        config: {},
      });
      setModalState({ type: "webhook-generate" });
    } else {
      setModalState({
        type: "account-connect",
        selectedApp: modalState.selectedApp,
      });

      updateNode(selectedNode.id, {
        ...selectedNode.data,
        appId: modalState.selectedApp,
        triggerId,
        isConfigured: false,
        label: "Configure Trigger",
        config: selectedNode.data.config || {},
      });
    }
  };

  const handleWebhookGeneration = (webhookUrl: string) => {
    if (selectedNode) {
      configureNode(selectedNode.id, {
        ...selectedNode.data,
        isConfigured: true,
        config: {
          webhook: {
            webhookUrl,
            method: "POST",
            headers: {},
            authentication: {
              type: "none",
            },
            retryConfig: {
              maxRetries: 3,
              retryInterval: 60,
            },
          },
        },
      });
    }
  };

  const handleSave = useCallback(async () => {
    if (!validateWorkflow()) {
      toast.error("Workflow is not valid");
      return;
    }
    if (!currentWorkflow?.id) {
      toast.error("No workflow selected");
      return;
    }
    setIsSaving(true);
    try {
      await updateWorkflow(currentWorkflow.id, {
        workflow_data: { nodes, edges },
      });
      toast.success("Workflow saved successfully");
    } catch (error) {
      console.error(error);
      toast.error("Failed to save workflow");
    } finally {
      setIsSaving(false);
    }
  }, [validateWorkflow, currentWorkflow?.id, nodes, edges, updateWorkflow]);

  const handleExecute = useCallback(() => {
    if (!validateWorkflow()) return;
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
            addNode({
              ...nodeToCopy,
              id: `${nodeToCopy.type}-${Date.now()}`,
              position: {
                x: nodeToCopy.position.x + 50,
                y: nodeToCopy.position.y + 50,
              },
            });
          }
          break;
        case "note":
          setModalState({ type: "note", nodeId });
          break;
      }
    },
    [nodes, addNode]
  );

  // Node wrapper components
  const nodeTypes: NodeTypes = {
    trigger: (props: NodeProps) => (
      <TriggerNode
        {...(props as any)}
        isValidConnection={() => true}
        onAction={(action) => handleNodeAction(action, props.id)}
      />
    ),
    action: (props: NodeProps) => (
      <ActionNode
        {...(props as any)}
        isValidConnection={() => true}
        onAction={(action: NodeAction) => handleNodeAction(action, props.id)}
      />
    ),
    condition: (props: NodeProps) => (
      <ConditionNode {...(props as any)} isValidConnection={() => true} />
    ),
  };

  useEffect(() => {
    if (nodes.length === 0) {
      setNodes([
        {
          id: "trigger-1",
          type: "trigger",
          position: { x: window.innerWidth / 3, y: 100 },
          data: {
            label: "Choose a trigger app",
            description: "Click to start configuring your workflow",
            isValid: false,
            isConfigured: false,
            config: {},
            outputSchema: { type: "object", properties: {} },
          },
        },
      ]);
    }
  }, [nodes.length]);

  return (
    <div className="flex h-screen bg-gray-50">
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
          isSaving={isSaving}
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
        onSelectTrigger={handleTriggerSelection}
      />

      <AccountConnectionModal
        isOpen={modalState.type === "account-connect"}
        onClose={() => setModalState({ type: null })}
        appId={modalState.selectedApp!}
        onConnect={() => {
          setModalState({ type: null });
          if (selectedNode) {
            updateNode(selectedNode.id, { isConfigured: true });
          }
        }}
      />

      <WebhookGenerationModal
        isOpen={modalState.type === "webhook-generate"}
        onClose={() => setModalState({ type: null })}
        onGenerate={handleWebhookGeneration}
      />

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
