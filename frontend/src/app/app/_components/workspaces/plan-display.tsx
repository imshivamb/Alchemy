import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export const PlanDisplay = ({ plan }: { plan: string }) => (
  <div className="flex items-center justify-between">
    <div className="space-y-1">
      <h4 className="text-sm font-medium">Current Plan</h4>
      <div className="flex items-center gap-2">
        <Badge
          variant={plan === "free" ? "secondary" : "default"}
          className="capitalize"
        >
          {plan}
        </Badge>
        {plan === "free" && (
          <Button variant="outline" size="sm">
            Upgrade Plan
          </Button>
        )}
      </div>
    </div>
  </div>
);
