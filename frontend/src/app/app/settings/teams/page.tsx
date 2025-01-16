"use client";

import { useEffect } from "react";

import { useRouter } from "next/navigation";
import { Separator } from "@/components/ui/separator";

import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useTeamStore } from "@/stores/team.store";
import { TeamSettings } from "../../teams/[teamId]/_components/team-settings";

export default function TeamSettingsPage({
  params,
}: {
  params: { teamId: string };
}) {
  const { getTeamById, currentTeam, isLoading } = useTeamStore();
  const router = useRouter();

  useEffect(() => {
    getTeamById(params.teamId);
  }, [params.teamId, getTeamById]);

  if (isLoading || !currentTeam) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push(`/teams/${params.teamId}`)}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Team
            </Button>
          </div>
          <h2 className="text-2xl font-bold">Team Settings</h2>
          <p className="text-muted-foreground">
            Manage {currentTeam.name} team settings and preferences
          </p>
        </div>
      </div>

      <Separator />

      <TeamSettings team={currentTeam} />
    </div>
  );
}
