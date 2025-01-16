"use client";

import * as React from "react";
import { Building2, ChevronsUpDown, Plus } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { useRouter } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useWorkspaceStore } from "@/stores/workspace.store";

export function WorkspaceSwitcher() {
  const { isMobile } = useSidebar();
  const router = useRouter();
  const {
    currentWorkspace,
    workspaces,
    setCurrentWorkspace,
    isLoading,
    fetchWorkspaces,
  } = useWorkspaceStore();

  const [showUpgradeModal, setShowUpgradeModal] = React.useState(false);

  // Fetch workspaces on mount
  React.useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const handleWorkspaceChange = (workspace: (typeof workspaces)[0]) => {
    setCurrentWorkspace(workspace);
  };

  const handleAddWorkspace = () => {
    // Check if user is on free plan
    const hasActiveWorkspace = workspaces.some((w) => w.plan_type === "free");
    if (hasActiveWorkspace) {
      setShowUpgradeModal(true);
    } else {
      router.push("/app/workspaces/new");
    }
  };

  if (!currentWorkspace || isLoading) return null;

  return (
    <>
      <SidebarMenu>
        <SidebarMenuItem>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <SidebarMenuButton
                size="lg"
                className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              >
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Building2 className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">
                    {currentWorkspace.name}
                  </span>
                  <span className="truncate text-xs capitalize">
                    {currentWorkspace.plan_type} Plan
                  </span>
                </div>
                <ChevronsUpDown className="ml-auto" />
              </SidebarMenuButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
              align="start"
              side={isMobile ? "bottom" : "right"}
              sideOffset={4}
            >
              <DropdownMenuLabel className="text-xs text-muted-foreground">
                Workspaces
              </DropdownMenuLabel>
              {workspaces.map((workspace) => (
                <DropdownMenuItem
                  key={workspace.id}
                  onClick={() => handleWorkspaceChange(workspace)}
                  className="gap-2 p-2"
                >
                  <div className="flex size-6 items-center justify-center rounded-sm border">
                    <Building2 className="size-4 shrink-0" />
                  </div>
                  {workspace.name}
                  <span className="ml-auto text-xs capitalize text-muted-foreground">
                    {workspace.role}
                  </span>
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="gap-2 p-2"
                onClick={handleAddWorkspace}
              >
                <div className="flex size-6 items-center justify-center rounded-md border bg-background">
                  <Plus className="size-4" />
                </div>
                <div className="font-medium text-muted-foreground">
                  Add workspace
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>

      <Dialog open={showUpgradeModal} onOpenChange={setShowUpgradeModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upgrade to Add More Workspaces</DialogTitle>
            <DialogDescription>
              Free plan is limited to one workspace. Upgrade to Business or
              Enterprise plan to create additional workspaces.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-4 mt-6">
            <Button
              variant="outline"
              onClick={() => setShowUpgradeModal(false)}
            >
              Cancel
            </Button>
            <Button onClick={() => router.push("/app/pricing")}>
              View Pricing
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
