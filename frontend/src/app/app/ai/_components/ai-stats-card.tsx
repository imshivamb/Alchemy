import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAIStore } from "@/stores/ai.store";

export function AIStatsCards() {
  const { tasks } = useAIStore();

  const stats = {
    total: tasks.length,
    active: tasks.filter((t) => ["pending", "processing"].includes(t.status))
      .length,
    completed: tasks.filter((t) => t.status === "completed").length,
    failed: tasks.filter((t) => t.status === "failed").length,
  };

  const successRate = stats.total
    ? ((stats.completed / stats.total) * 100).toFixed(1)
    : "0";

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 p-4">
      <StatCard title="Total Tasks" value={stats.total} />
      <StatCard title="Active Tasks" value={stats.active} />
      <StatCard title="Success Rate" value={`${successRate}%`} />
      <StatCard title="Failed Tasks" value={stats.failed} />
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: string | number }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );
}
