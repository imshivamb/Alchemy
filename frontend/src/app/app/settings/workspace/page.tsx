import React from "react";
import { PageHeader } from "../../_components/page-header";
import { Separator } from "@/components/ui/separator";
import { WorkspaceOverview } from "../../_components/workspaces/workspace-overview";
import { WorkspacePreferences } from "../../_components/workspaces/workspace-preference";
import { TeamsOverview } from "../../_components/workspaces/team-overview";

export default function WorkspaceSettings() {
  return (
    <div className="space-y-6">
      <PageHeader
        heading="Workspace"
        text="Manage your workspace preferences and view usage statistics."
      />
      <Separator />

      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <WorkspaceOverview />
          <WorkspacePreferences />
        </div>
        <TeamsOverview />
      </div>
    </div>
  );
}
