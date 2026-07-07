
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AdminDashboard } from "./views/AdminDashboard";
import { PrivacyInbox } from "./views/PrivacyInbox";
import { FOISubmitForm } from "./views/FOISubmitForm";
import { DataInventoryForm } from "./views/DataInventoryForm";
import { MeetingCreateForm } from "./views/MeetingCreateForm";
import { TrustTiers } from "./views/TrustTiers";
import { DeploymentCenter } from "./views/DeploymentCenter";
import { PublicWidget } from "./views/PublicWidget";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/widget" element={<PublicWidget />} />

        {/* Dashboard Shell with Nested Routes */}
        <Route path="/" element={<AdminDashboard />}>
          <Route index element={<Navigate to="/inbox" replace />} />
          <Route path="inbox" element={<PrivacyInbox />} />
          <Route path="foi-submit" element={<FOISubmitForm />} />
          <Route path="inventory" element={<DataInventoryForm />} />
          <Route path="meetings" element={<MeetingCreateForm />} />
          <Route path="trust-tiers" element={<TrustTiers />} />
          <Route path="deployment" element={<DeploymentCenter />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
