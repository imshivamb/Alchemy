import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { formatDistanceToNow } from "date-fns";
import { RefreshCw } from "lucide-react";
import { FastAPIWebhook, WebhookDelivery } from "@/types/webhook.types";
import { useState, useEffect } from "react";
import { useWebhookStore } from "@/stores/webhook.store";

export function WebhookDeliveryHistory({
  webhook,
}: {
  webhook: FastAPIWebhook;
}) {
  const [deliveries, setDeliveries] = useState<WebhookDelivery[]>([]);
  const { getDeliveries } = useWebhookStore();

  useEffect(() => {
    loadDeliveries();
  }, [webhook.id]);

  const loadDeliveries = async () => {
    const data = await getDeliveries(webhook.id);
    if (data) setDeliveries(data);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button variant="outline" size="sm" onClick={loadDeliveries}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Time</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Response</TableHead>
            <TableHead>Duration</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {deliveries.map((delivery) => (
            <TableRow key={delivery.id}>
              <TableCell>
                {formatDistanceToNow(new Date(delivery.created_at), {
                  addSuffix: true,
                })}
              </TableCell>
              <TableCell>
                <span
                  className={`px-2 py-1 rounded-full text-sm ${
                    delivery.status === "success"
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {delivery.status}
                </span>
              </TableCell>
              <TableCell>{delivery.response?.status_code || "-"}</TableCell>
              <TableCell>{delivery.duration}ms</TableCell>
              <TableCell className="text-right">
                <Button variant="ghost" size="sm" onClick={() => {}}>
                  View Details
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
