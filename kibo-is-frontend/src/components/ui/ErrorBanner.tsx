import React from "react";
import { AlertTriangle } from "lucide-react";

export const ErrorBanner = ({ error }: { error: string }) => (
  <div className="bg-red-900/20 border border-red-900/50 rounded-lg p-4 flex items-start text-red-200 mb-6">
    <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
    <p>{error}</p>
  </div>
);\n