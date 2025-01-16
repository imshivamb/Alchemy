import { Progress } from "@/components/ui/progress";

export const UsageStats = ({
  title,
  current,
  limit,
}: {
  title: string;
  current: number;
  limit: number;
}) => (
  <div className="space-y-2">
    <div className="flex justify-between text-sm">
      <span className="font-medium">{title}</span>
      <span>
        {current} / {limit}
      </span>
    </div>
    <Progress value={(current / limit) * 100} className="h-2" />
  </div>
);
