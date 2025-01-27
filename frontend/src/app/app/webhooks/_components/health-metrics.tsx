import { Card } from "@/components/ui/card";
import { FastAPIWebhook } from "@/types/webhook.types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export function WebhookHealthMetrics({ webhook }: { webhook: FastAPIWebhook }) {
  const successRate = webhook.total_deliveries
    ? (webhook.successful_deliveries / webhook.total_deliveries) * 100
    : 0;

  // Default data if no metrics available
  //   const defaultData = [{ timestamp: new Date().toISOString(), duration: 0 }];

  return (
    <div className="space-y-6">
      <Card className="p-4">
        <h3 className="text-lg font-medium mb-4">Success Rate</h3>
        <div className="flex items-center justify-center">
          <div className="relative h-32 w-32">
            {/* Circular progress indicator */}
            <svg className="h-full w-full" viewBox="0 0 100 100">
              <circle
                className="text-gray-200"
                strokeWidth="10"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
              />
              <circle
                className="text-blue-600"
                strokeWidth="10"
                strokeDasharray={`${successRate * 2.51327}, 251.327`}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
              />
            </svg>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <span className="text-2xl font-bold">
                {successRate.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-4">
        <h3 className="text-lg font-medium mb-4">Response Times</h3>
        {webhook.metrics?.response_times &&
        webhook.metrics.response_times.length > 0 ? (
          <LineChart
            width={500}
            height={300}
            data={webhook.metrics.response_times}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="duration" stroke="#3b82f6" />
          </LineChart>
        ) : (
          <div className="text-center text-muted-foreground py-8">
            No response time data available
          </div>
        )}
      </Card>
    </div>
  );
}
