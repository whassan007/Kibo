import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LegacyApp from "./legacy/App";
import { ToastProvider } from "./components/ui/ToastContext";
import { PrivacyOSPortal } from "./views/PrivacyOSPortal";

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Routes>
          <Route path="/privacy-os/*" element={<PrivacyOSPortal />} />
          <Route path="/*" element={<LegacyApp />} />
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}
