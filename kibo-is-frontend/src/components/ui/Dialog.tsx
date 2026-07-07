import React, { useEffect, useRef } from "react";
import { AlertOctagon, X } from "lucide-react";
import { Button } from "./Button";

export interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description: string;
  confirmText?: string;
  onConfirm?: () => void;
  isDestructive?: boolean;
}

export const Dialog: React.FC<DialogProps> = ({ 
  isOpen, onClose, title, description, confirmText = "OK", onConfirm, isDestructive = false 
}) => {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      if (!dialog.open) dialog.showModal();
    } else {
      if (dialog.open) dialog.close();
    }
  }, [isOpen]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    const handleCancel = (e: Event) => {
      e.preventDefault();
      onClose();
    };
    
    dialog.addEventListener("cancel", handleCancel);
    return () => dialog.removeEventListener("cancel", handleCancel);
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <dialog 
      ref={dialogRef}
      className="backdrop:bg-black/80 bg-neutral-900 border border-neutral-800 rounded-lg shadow-2xl p-0 w-full max-w-md m-auto text-white"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-desc"
    >
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            {isDestructive && <AlertOctagon className="text-red-500 w-6 h-6" />}
            <h2 id="dialog-title" className="text-xl font-semibold">{title}</h2>
          </div>
          <button 
            type="button" 
            onClick={onClose}
            className="text-neutral-400 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 rounded p-1"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div id="dialog-desc" className="text-neutral-300 mb-6">
          {description}
        </div>
        <div className="flex justify-end gap-3">
          {onConfirm && (
            <Button variant="ghost" onClick={onClose}>Cancel</Button>
          )}
          <Button 
            variant={isDestructive ? "danger" : "primary"} 
            onClick={() => {
              if (onConfirm) onConfirm();
              onClose();
            }}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </dialog>
  );
};\n