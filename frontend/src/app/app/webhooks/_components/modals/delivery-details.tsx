import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { WebhookDelivery } from "@/types/webhook.types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";

interface DeliveryDetailsModalProps {
  open: boolean;
  onClose: () => void;
  delivery: WebhookDelivery;
}

export function DeliveryDetailsModal({
  open,
  onClose,
  delivery,
}: DeliveryDetailsModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Delivery Details</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status and Timing */}
          <div className="flex justify-between items-center">
            <Badge
              variant={
                delivery.status === "default" ? "default" : "destructive"
              }
            >
              {delivery.status}
            </Badge>
            <span className="text-sm text-muted-foreground">
              {formatDistanceToNow(new Date(delivery.created_at), {
                addSuffix: true,
              })}
            </span>
          </div>

          {/* Request Details */}
          <Card className="p-4">
            <h3 className="font-medium mb-2">Request</h3>
            <div className="space-y-2">
              <div>
                <h4 className="text-sm font-medium">Headers</h4>
                <pre className="text-sm bg-muted p-2 rounded">
                  {JSON.stringify(delivery.headers, null, 2)}
                </pre>
              </div>
              <div>
                <h4 className="text-sm font-medium">Payload</h4>
                <pre className="text-sm bg-muted p-2 rounded">
                  {JSON.stringify(delivery.payload, null, 2)}
                </pre>
              </div>
            </div>
          </Card>

          {/* Response Details */}
          <Card className="p-4">
            <h3 className="font-medium mb-2">Response</h3>
            <div className="space-y-2">
              {delivery.response ? (
                <>
                  <div>
                    <h4 className="text-sm font-medium">Status Code</h4>
                    <p>{delivery.response.status_code}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium">Body</h4>
                    <pre className="text-sm bg-muted p-2 rounded">
                      {JSON.stringify(delivery.response.body, null, 2)}
                    </pre>
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No response received
                </p>
              )}
            </div>
          </Card>

          {/* Error Details */}
          {delivery.error && (
            <Card className="p-4 border-destructive">
              <h3 className="font-medium mb-2 text-destructive">Error</h3>
              <p className="text-sm">{delivery.error}</p>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
