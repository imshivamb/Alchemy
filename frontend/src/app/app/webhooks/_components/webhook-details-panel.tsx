import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FastAPIWebhook } from "@/types/webhook.types";
import { X } from "lucide-react";
import { WebhookHealthMetrics } from "./health-metrics";
import { WebhookDeliveryHistory } from "./webhook-delivery-history";
import { WebhookConfiguration } from "./webhook-configuration";

interface WebhookDetailsPanelProps {
  webhook: FastAPIWebhook;
  onClose: () => void;
}

export function WebhookDetailsPanel({
  webhook,
  onClose,
}: WebhookDetailsPanelProps) {
  return (
    <div className="w-[600px] border-l bg-background p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">{webhook.name}</h2>
        <button onClick={onClose}>
          <X className="h-4 w-4" />
        </button>
      </div>

      <Tabs defaultValue="config">
        <TabsList className="w-full">
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="health">Health</TabsTrigger>
          <TabsTrigger value="deliveries">Deliveries</TabsTrigger>
        </TabsList>

        <TabsContent value="config">
          <WebhookConfiguration webhook={webhook} />
        </TabsContent>

        <TabsContent value="health">
          <WebhookHealthMetrics webhook={webhook} />
        </TabsContent>

        <TabsContent value="deliveries">
          <WebhookDeliveryHistory webhook={webhook} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
