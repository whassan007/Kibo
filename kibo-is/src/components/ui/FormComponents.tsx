
import React from "react";
export const TextField = ({ label, error, ...props }) => (
  <div className="mb-4">
    <label className="block mb-1 font-semibold">{label}</label>
    <input className={`border rounded p-2 w-full ${error ? "border-red-500" : "border-gray-300"}`} {...props} />
    {error && <span className="text-red-500 text-sm mt-1">{error}</span>}
  </div>
);
