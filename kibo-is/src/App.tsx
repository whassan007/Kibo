import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastProvider } from "./components/ui/ToastContext";
import { PrivacyOSPortal } from "./views/PrivacyOSPortal";

const LegacyApp = lazy(() => import("./legacy/App"));

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Suspense
          fallback={
            <div className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center text-xs font-mono">
              Loading KIBO Privacy OS Workspace...
            </div>
          }
        >
          <Routes>
            <Route path="/privacy-os/*" element={<PrivacyOSPortal />} />
            <Route path="/" element={<PrivacyOSPortal />} />
            <Route path="/legacy/*" element={<LegacyApp />} />
          </Routes>
        </Suspense>
      </ToastProvider>
    </BrowserRouter>
  );
}
