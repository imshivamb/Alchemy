import { Card } from "@/components/ui/card";
import { useAIStore } from "@/stores/ai.store";
import { AIModel } from "@/types/ai.types";

interface ModelsPanelProps {
  models: AIModel[];
}
export function ModelsPanel({}: ModelsPanelProps) {
  const { models } = useAIStore();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {models.map((model) => (
        <Card key={model.id} className="p-4">
          <h3 className="font-semibold">{model.name}</h3>
          <div className="mt-2 space-y-1 text-sm">
            <p>Max Tokens: {model.max_tokens}</p>
            <p>Cost: ${model.cost_per_token}/token</p>
            <div className="mt-2">
              <p className="font-medium">Recommended for:</p>
              <ul className="list-disc list-inside">
                {model.recommended_uses.map((use, i) => (
                  <li key={i}>{use}</li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
