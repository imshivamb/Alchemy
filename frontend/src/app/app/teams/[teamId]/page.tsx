"use client";

import { use, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TeamMembers } from "./_components/team-members";
import { TeamSettings } from "./_components/team-settings";
import { TeamOverview } from "./_components/team-overview";
import { useTeamStore } from "@/stores/team.store";
import { Suspense } from "react";
import { PageHeader } from "../../_components/page-header";
import { Separator } from "@/components/ui/separator";

interface Props {
  params: Promise<{ teamId: string }>;
}

function TeamContent({ teamId }: { teamId: string }) {
  const { getTeamById, currentTeam, isLoading } = useTeamStore();

  useEffect(() => {
    if (teamId) {
      getTeamById(teamId).catch(console.error);
    }
  }, [teamId, getTeamById]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <p>Loading team details...</p>
      </div>
    );
  }

  if (!currentTeam) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <p>Team not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader heading={currentTeam.name} text={currentTeam.description} />
      <Separator />
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="members">Members</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="space-y-4">
          <TeamOverview team={currentTeam} />
        </TabsContent>
        <TabsContent value="members" className="space-y-4">
          <TeamMembers team={currentTeam} />
        </TabsContent>
        <TabsContent value="settings" className="space-y-4">
          <TeamSettings team={currentTeam} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function TeamDetailsPage({ params }: Props) {
  const resolvedParams = use(params);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <TeamContent teamId={resolvedParams.teamId} />
    </Suspense>
  );
}
