import React from "react";
import { Layers } from "lucide-react";

export const EmptyState = ({ title = "No Data", description = "There are currently no items to display." }) => (
  <div className="flex flex-col items-center justify-center p-12 text-neutral-400 border border-dashed border-neutral-800 rounded-lg">
    <Layers className="w-12 h-12 mb-4 text-neutral-600" />
    <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
    <p>{description}</p>
  </div>
);\n