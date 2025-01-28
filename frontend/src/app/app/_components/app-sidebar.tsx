"use client";

import * as React from "react";
import {
  Home,
  Workflow,
  Puzzle,
  Bot,
  Webhook,
  LineChart,
  Users,
  Key,
  Settings2,
  Plus,
} from "lucide-react";

import { NavMain } from "./nav-main";
import { NavUser } from "./nav-user";
import { WorkspaceSwitcher } from "./workspace-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useWorkflowApiStore } from "@/stores/workflow-api.store";
import axios, { AxiosError } from "axios";
import { WorkflowLimitModal } from "@/components/workflow-builder/_components/modals/workflow-limil-modal";

const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Home",
      url: "/app/home",
      icon: Home,
      isActive: true,
    },
    {
      title: "Workflows",
      url: "/app/workflows",
      icon: Workflow,
    },
    {
      title: "Integrations",
      url: "/app/integrations",
      icon: Puzzle,
    },
    {
      title: "AI Tasks",
      url: "/app/ai",
      icon: Bot,
    },
    {
      title: "Web3 Tasks",
      url: "/app/web3",
      icon: Bot,
    },
    {
      title: "Webhooks",
      url: "/app/webhooks",
      icon: Webhook,
    },
    {
      title: "Analytics",
      url: "/app/analytics",
      icon: LineChart,
    },
    {
      title: "Teams",
      url: "/app/teams",
      icon: Users,
    },
    {
      title: "API Keys",
      url: "/app/api-keys",
      icon: Key,
    },
    {
      title: "Settings",
      url: "/app/settings",
      icon: Settings2,
      items: [
        {
          title: "Profile",
          url: "/app/settings/profile",
        },
        {
          title: "Security",
          url: "/app/settings/security",
        },
        {
          title: "Workspaces",
          url: "/app/settings/workspace",
        },
        {
          title: "Teams",
          url: "/app/settings/teams",
        },
        {
          title: "Notifications",
          url: "/app/settings/notifications",
        },
      ],
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const router = useRouter();
  const { state } = useSidebar();
  const { createWorkflow } = useWorkflowApiStore();
  const [limitError, setLimitError] = React.useState<{
    current_count: number;
    max_allowed: number;
    plan: string;
  } | null>(null);

  const handleCreateWorkflow = async () => {
    try {
      const workflowData = {
        name: "Untitled Workflow",
        description: "",
        is_active: true,
        workflow_data: {},
      };

      const newWorkflow = await createWorkflow(workflowData);
      router.push(`/editor/${newWorkflow.id}`);
    } catch (error: AxiosError | any) {
      if (axios.isAxiosError(error)) {
        // Now we should have access to the error response
        console.log("Error response:", error.response?.data);

        if (error.response?.data) {
          const errorData = error.response.data;
          setLimitError({
            current_count: parseInt(errorData.current_count[0]),
            max_allowed: parseInt(errorData.max_allowed[0]),
            plan: errorData.plan[0],
          });
        }
      }
    }
  };
  return (
    <>
      <Sidebar collapsible="icon" {...props}>
        <SidebarHeader>
          <WorkspaceSwitcher />
          <Button
            className="w-full"
            size={state === "expanded" ? "lg" : "icon"}
            onClick={handleCreateWorkflow}
          >
            <Plus className={state === "expanded" ? "mr-2" : ""} size={16} />
            {state === "expanded" && <span> Create Workflow</span>}
          </Button>
        </SidebarHeader>
        <SidebarContent>
          <NavMain items={data.navMain} />
        </SidebarContent>
        <SidebarFooter>
          <NavUser />
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
      <WorkflowLimitModal
        isOpen={limitError !== null}
        onClose={() => setLimitError(null)}
        limitInfo={limitError || { current_count: 0, max_allowed: 0, plan: "" }}
      />
    </>
  );
}
