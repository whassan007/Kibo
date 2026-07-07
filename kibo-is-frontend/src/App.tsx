
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PrivacyInbox } from "./views/PrivacyInbox";
import { PublicWidget } from "./views/PublicWidget";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/inbox" element={<PrivacyInbox />} />
        <Route path="/widget" element={<PublicWidget />} />
      </Routes>
    </BrowserRouter>
  );
}
