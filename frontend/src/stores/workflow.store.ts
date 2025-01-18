import { create } from "zustand";
import { AppConnection, WorkflowNode } from "@/types/workflow.types";
import { addEdge, applyEdgeChanges, applyNodeChanges, Connection, Edge, EdgeChange, Node, NodeChange } from "@xyflow/react";
import { validationWorkflow } from "@/utils/workflow-vaildation";



interface WorkflowState {
    nodes: Node[];
    edges: Edge[];
    selectedNode: WorkflowNode | null;
    isValid: boolean;
    validationErrors: string[];
    isDirty: boolean;
    modalState: {
      type: 'app-select' | 'trigger-select' | 'action-select' | 'account-connect' | null;
      selectedApp?: string;
      selectedTrigger?: string;
      selectedAction?: string;
      step?: 'trigger' | 'action';
    };
    connections: AppConnection[];

    // NOde Operations
    setNodes: (nodes: Node[]) => void;
    onNodeChange: (node: NodeChange[]) => void;
    addNode: (node: Node) => void;
    updateNode: (nodeId: string, data: Partial<WorkflowNode['data']>) => void;
    deleteNode: (nodeId: string) => void;

    //Edge Operations
    setEdges: (edges: Edge[]) => void;
    onEdgesChange: (edges: EdgeChange[]) => void;
    onConnect: (connection: Connection) => void;

    //Set Selected Node
    setSelectedNode: (node: WorkflowNode | null) => void;

    //Workflow Operations
    validateWorkflow: () => boolean;
    resetWorkflow: () => void;
    loadWorkflow: (workflow: {nodes: Node[], edges: Edge[]}) => void;

    setModalState: (state: WorkflowState['modalState']) => void;
    addConnection: (connection: AppConnection) => void;
    removeConnection: (connectionId: string) => void;
    getConnectionsForApp: (appId: string) => AppConnection[];
    configureNode: (nodeId: string, config: {
      appId?: string;
      triggerId?: string;
      actionId?: string;
      connectionId?: string;
      config?: Record<string, any>;
    }) => void;

}

const defaultState = {
    nodes: [],
    edges: [],
    selectedNode: null,
    isValid: true,
    validationErrors: [],
    isDirty: false,
    modalState: { type: null },
    connections: [],
}

export const useWorkflowState = create<WorkflowState>((set, get) => ({
    ...defaultState,

    setModalState: (modalState) => set({ modalState }),

  addConnection: (connection) => 
    set((state) => ({
      connections: [...state.connections, connection]
    })),

  removeConnection: (connectionId) =>
    set((state) => ({
      connections: state.connections.filter(c => c.id !== connectionId)
    })),

  getConnectionsForApp: (appId) => 
    get().connections.filter(c => c.appId === appId),

  configureNode: (nodeId, config) => {
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: {
                ...node.data,
                ...config,
                isConfigured: true,
                isValid: true
              }
            }
          : node
      ),
      isDirty: true
    }));
    get().validateWorkflow();
  },
    setNodes: (nodes) => {
        set({ nodes, isDirty: true });
        get().validateWorkflow();
    },

    onNodeChange: (changes) => {
        set((state) => ({
            nodes: applyNodeChanges(changes, state.nodes),
            isDirty: true,
        }));
        get().validateWorkflow();
    },
    
    addNode: (node)=> {
        set((state) => ({
            nodes: [...state.nodes, node],
            isDirty: true,
        }));
        get().validateWorkflow();
    },

    updateNode: (nodeId, data) => {
        set((state) => ({
          nodes: state.nodes.map((node) =>
            node.id === nodeId
              ? { ...node, data: { ...node.data, ...data } }
              : node
          ),
          isDirty: true
        }));
        get().validateWorkflow();
    },

    deleteNode: (nodeId) => {
        set((state) => ({
          nodes: state.nodes.filter((node) => node.id !== nodeId),
          edges: state.edges.filter(
            (edge) => edge.source !== nodeId && edge.target !== nodeId
          ),
          selectedNode: state.selectedNode?.id === nodeId ? null : state.selectedNode,
          isDirty: true
        }));
        get().validateWorkflow();
    },

    setEdges: (edges) => {
        set({ edges, isDirty: true });
        get().validateWorkflow();
    },

    onEdgesChange: (changes) => {
        set((state) => ({
          edges: applyEdgeChanges(changes, state.edges),
          isDirty: true
        }));
        get().validateWorkflow();
    },

    onConnect: (connection) => {
        set((state) => ({
          edges: addEdge(connection, state.edges),
          isDirty: true
        }));
        get().validateWorkflow();
    },

    setSelectedNode: (node) => {
        set({ selectedNode: node });
    },

    validateWorkflow: () => {
        const { nodes, edges } = get();
        const validationResult = validationWorkflow(nodes, edges);
        set({
            isValid: validationResult.isValid,
            validationErrors: validationResult.errors,
        });
        return validationResult.isValid;
    },
    resetWorkflow: () => {
        set({
          ...defaultState,
          isDirty: false
        });
      },
    
    loadWorkflow: (workflow) => {
        set({
          nodes: workflow.nodes,
          edges: workflow.edges,
          selectedNode: null,
          isDirty: false
        });
        get().validateWorkflow();
    }
}))