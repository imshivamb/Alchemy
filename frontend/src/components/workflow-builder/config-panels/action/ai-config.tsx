import { AIConfig as AIConfigType } from "@/types/workflow.types";
import React from "react";

type AIConfigProps = {
  config: AIConfigType;
  onChange: (config: AIConfigType) => void;
};

const AIConfig = ({ config, onChange }: AIConfigProps) => {
  return <div>AIConfig</div>;
};

export default AIConfig;
