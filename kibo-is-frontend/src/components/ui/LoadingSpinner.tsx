import React from "react";
import { RefreshCw } from "lucide-react";

export const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center p-12 text-neutral-400">
    <RefreshCw className="w-8 h-8 animate-spin mb-4 text-amber-500" />
    <p>Loading data...</p>
  </div>
);\n