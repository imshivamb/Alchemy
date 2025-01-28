import { Card } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Loading..." }: LoadingStateProps) {
  return (
    <Card className="flex items-center justify-center h-[400px]">
      <div className="text-center">
        <LoadingSpinner />
        <p className="text-muted-foreground">{message}</p>
      </div>
    </Card>
  );
}
