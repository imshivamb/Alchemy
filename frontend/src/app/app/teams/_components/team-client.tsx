"use client";

import { useEffect } from "react";

import { CreateTeamButton } from "./create-team-button";
import { useTeamStore } from "@/stores/team.store";
import { useWorkspaceStore } from "@/stores/workspace.store";
import { TeamsTable } from "./teams-data-table";
import { columns } from "./teams-data-table/columns";
import { PageHeader } from "../../_components/page-header";
import { Separator } from "@/components/ui/separator";

export function TeamsClient() {
  const { teams, fetchTeams } = useTeamStore();
  const { currentWorkspace } = useWorkspaceStore();

  useEffect(() => {
    if (currentWorkspace?.id) {
      fetchTeams(currentWorkspace.id);
    }
  }, [currentWorkspace?.id, fetchTeams]);

  return (
    <div className="space-y-6 p-4 md:p-10 pb-8 md:pb-16">
      <div className="flex justify-between ">
        <PageHeader
          heading="Teams"
          text="Manage your teams and team members."
        />
        <CreateTeamButton />
      </div>
      <Separator />

      <TeamsTable columns={columns} data={teams} />
    </div>
  );
}
