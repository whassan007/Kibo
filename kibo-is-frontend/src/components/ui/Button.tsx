import React, { ButtonHTMLAttributes } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
}

export const Button: React.FC<ButtonProps> = ({ variant = "primary", className = "", ...props }) => {
  const base = "px-4 py-2 font-medium rounded-md focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors";
  
  const variants = {
    primary: "bg-white text-black hover:bg-neutral-200",
    secondary: "bg-neutral-800 text-white hover:bg-neutral-700 border border-neutral-700",
    danger: "bg-red-900/50 text-red-200 hover:bg-red-900",
    ghost: "bg-transparent text-neutral-300 hover:text-white hover:bg-neutral-800"
  };

  return (
    <button 
      type={props.type || "button"}
      className={`${base} ${variants[variant]} ${className}`} 
      {...props} 
    />
  );
};\n