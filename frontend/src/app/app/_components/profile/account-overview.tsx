"use client";

import { AuthStore } from "@/stores/auth.store";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

export function AccountOverview() {
  const user = AuthStore((state) => state.user);

  if (!user) return null;

  const statusColorMap = {
    active: "bg-green-100 text-green-700",
    suspended: "bg-yellow-100 text-yellow-700",
    cancelled: "bg-red-100 text-red-700",
  };

  const accountItems = [
    {
      label: "Account Status",
      value: user.profile.account_status,
      badge: true,
      badgeColor:
        statusColorMap[
          user.profile.account_status as keyof typeof statusColorMap
        ],
    },
    {
      label: "Email Verification",
      value: user.is_verified ? "Verified" : "Unverified",
      badge: true,
      badgeColor: user.is_verified
        ? "bg-green-100 text-green-700"
        : "bg-yellow-100 text-yellow-700",
    },
    {
      label: "Plan Type",
      value: user.profile.plan_type,
      badge: false,
    },
    {
      label: "Member Since",
      value: format(new Date(user.created_at), "MMMM d, yyyy"),
      badge: false,
    },
    {
      label: "Workflow Limit",
      value: `${user.profile.max_workflows} workflows`,
      badge: false,
    },
    {
      label: "Last Updated",
      value: format(new Date(user.updated_at), "MMMM d, yyyy"),
      badge: false,
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account Overview</CardTitle>
        <CardDescription>
          View your account status and information
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {accountItems.map((item, index) => (
            <div key={item.label}>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm font-medium text-muted-foreground">
                  {item.label}
                </span>
                {item.badge ? (
                  <Badge className={cn("font-medium", item.badgeColor)}>
                    {item.value.charAt(0).toUpperCase() + item.value.slice(1)}
                  </Badge>
                ) : (
                  <span className="text-sm font-medium">{item.value}</span>
                )}
              </div>
              {index < accountItems.length - 1 && (
                <Separator className="mt-2" />
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
