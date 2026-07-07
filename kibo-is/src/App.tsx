import React from "react";
import { BrowserRouter } from "react-router-dom";
import LegacyApp from "./legacy/App";
import { ToastProvider } from "./components/ui/ToastContext";

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <LegacyApp />
      </ToastProvider>
    </BrowserRouter>
  );
}
