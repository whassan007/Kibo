import React, { HTMLAttributes } from "react";

export const Panel: React.FC<HTMLAttributes<HTMLDivElement>> = ({ className = "", ...props }) => (
  <div className={`bg-neutral-900 border border-neutral-800 rounded-lg p-6 ${className}`} {...props} />
);\n