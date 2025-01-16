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
} from "@/components/ui/sidebar";

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
      url: "/app/ai-tasks",
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
      title: "Team",
      url: "/app/team",
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
          title: "Notifications",
          url: "/app/settings/notifications",
        },
      ],
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <WorkspaceSwitcher />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
