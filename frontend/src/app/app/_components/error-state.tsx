import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <Card className="flex items-center justify-center h-[400px]">
      <div className="text-center">
        <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
        <p className="text-muted-foreground mb-4">{message}</p>
        {onRetry && <Button onClick={onRetry}>Try Again</Button>}
      </div>
    </Card>
  );
}
