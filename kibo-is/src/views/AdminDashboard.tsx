
import React from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

export const AdminDashboard: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { name: "Privacy Inbox", path: "/inbox" },
    { name: "FOI Request", path: "/foi-submit" },
    { name: "Data Inventory", path: "/inventory" },
    { name: "Meetings Planner", path: "/meetings" },
    { name: "Trust Tiers", path: "/trust-tiers" },
    { name: "Deployment Center", path: "/deployment" },
  ];

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Sidebar Navigation */}
      <nav className="w-64 bg-gray-900 text-white flex flex-col h-full shrink-0">
        <div className="p-4 font-bold text-xl border-b border-gray-800 tracking-wide text-indigo-400">
          KIBO.IS
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-3">
            {navItems.map(item => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`block px-3 py-2 rounded transition-colors ${
                    location.pathname === item.path
                      ? "bg-indigo-600 text-white"
                      : "text-gray-300 hover:bg-gray-800 hover:text-white"
                  }`}
                >
                  {item.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
          TS Twin v2.0
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto flex flex-col h-full bg-white shadow-inner">
        <header className="h-14 border-b flex items-center px-6 bg-white shrink-0 sticky top-0 z-10 shadow-sm">
           <h1 className="text-lg font-bold">Admin Console</h1>
        </header>
        <div className="p-6 flex-1">
          {/* Renders the routed child components here */}
          <Outlet />
        </div>
      </main>
    </div>
  );
};
