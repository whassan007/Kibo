import React, { InputHTMLAttributes, forwardRef } from "react";

export interface FieldProps extends InputHTMLAttributes<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement> {
  label: string;
  error?: string;
  as?: "input" | "textarea" | "select";
  options?: { label: string; value: string }[];
}

export const Field = forwardRef<any, FieldProps>(({ 
  label, error, as = "input", options, className = "", required, ...props 
}, ref) => {
  const id = props.id || props.name;
  
  const baseClasses = "w-full bg-neutral-900 border border-neutral-700 rounded-md px-3 py-2 text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-colors";
  const errorClasses = error ? "border-red-500 focus:ring-red-500" : "";
  
  return (
    <div className="mb-4">
      <label htmlFor={id} className="block text-sm font-medium text-neutral-300 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      
      {as === "select" ? (
        <select
          id={id}
          ref={ref}
          className={`${baseClasses} ${errorClasses} ${className}`}
          {...(props as any)}
        >
          {options?.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      ) : as === "textarea" ? (
        <textarea
          id={id}
          ref={ref}
          className={`${baseClasses} ${errorClasses} ${className}`}
          {...(props as any)}
        />
      ) : (
        <input
          id={id}
          ref={ref}
          className={`${baseClasses} ${errorClasses} ${className}`}
          {...(props as any)}
        />
      )}
      
      {error && (
        <p className="mt-1 text-sm text-red-500 flex items-center gap-1">
          <span aria-hidden="true">⚠</span> {error}
        </p>
      )}
    </div>
  );
});
Field.displayName = "Field";\n