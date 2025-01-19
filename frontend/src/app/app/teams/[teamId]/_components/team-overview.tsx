"use client";

import { TeamDetail } from "@/types/teams.types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UsersRound, UserPlus, Shield } from "lucide-react";

interface TeamOverviewProps {
  team: TeamDetail;
}

export function TeamOverview({ team }: TeamOverviewProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {/* Member Stats */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Members</CardTitle>
          <UsersRound className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {team.statistics?.total_members || team.members_count || 0}
          </div>
          <p className="text-xs text-muted-foreground">
            {team.statistics?.active_members || team.members_count || 0} active
            members
          </p>
        </CardContent>
      </Card>

      {/* Role Distribution */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Role Distribution
          </CardTitle>
          <Shield className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {team.statistics?.roles_distribution?.map((role) => (
              <div
                key={role.role}
                className="flex items-center justify-between"
              >
                <span className="text-sm capitalize">{role.role}</span>
                <span className="text-sm font-medium">{role.count}</span>
              </div>
            )) || (
              <div className="flex items-center justify-between">
                <span className="text-sm">No role data available</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Basic Info */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Team Info</CardTitle>
          <UserPlus className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div>
              <p className="text-sm text-muted-foreground">Owner</p>
              <p className="text-sm font-medium">{team.owner_email}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Created</p>
              <p className="text-sm font-medium">
                {new Date(team.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
