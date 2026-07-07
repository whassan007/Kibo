
import React, { useState, useEffect, useRef } from "react";
import { fetchInbox, submitDecision } from "../services/inboxService";
import { mockInboxItems } from "../fixtures/inbox";
import { DataRow } from "../components/inbox/DataRow";
import { TriageCard } from "../components/inbox/TriageCard";
import { EmptyState } from "../components/inbox/EmptyState";
import { OfflineBanner } from "../components/inbox/OfflineBanner";
import { Toast } from "../components/inbox/Toast";
import { SlaBadge } from "../components/inbox/SlaBadge";

export const PrivacyInbox = ({ useMocks = false }) => {
  const [items, setItems] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [toast, setToast] = useState<{msg: string, auditRef?: string} | null>(null);
  const [search, setSearch] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadInbox = async () => {
      setIsLoading(true);
      try {
        if (useMocks) {
          setItems(mockInboxItems);
        } else {
          const data = await fetchInbox("sla", "", search);
          setItems(data.items || []);
        }
        setIsOffline(false);
      } catch (err) {
        setIsOffline(true);
      } finally {
        setIsLoading(false);
      }
    };
    loadInbox();
  }, [search, useMocks]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === "INPUT" || document.activeElement?.tagName === "TEXTAREA") return;
      
      const idx = items.findIndex(i => i.id === selectedId);
      
      if (e.key === "j" && idx < items.length - 1) setSelectedId(items[idx + 1].id);
      if (e.key === "k" && idx > 0) setSelectedId(items[idx - 1].id);
      if (e.key === "/") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [items, selectedId]);

  const handleAction = async (action: string) => {
    if (!selectedId || isOffline) return;
    try {
      const res = await submitDecision(selectedId, action, "Automated decision from UI");
      setToast({ msg: `Action ${action} successful`, auditRef: res.audit_ref });
      setItems(items.filter(i => i.id !== selectedId));
      setSelectedId(null);
      setTimeout(() => setToast(null), 5000);
    } catch (err) {
      setErrorMsg("Failed to apply decision. Please try again.");
    }
  };

  return (
    <div className="flex h-screen bg-[#f8f9fa] text-[#111827]">
      {isOffline && <OfflineBanner />}
      {toast && <Toast msg={toast.msg} />}
      
      <div className="w-[300px] border-r border-[#e5e7eb] flex flex-col bg-white">
        <div className="p-4 border-b border-[#e5e7eb]">
          <h2 className="font-semibold text-lg mb-2">Privacy Inbox</h2>
          <input 
            ref={searchInputRef}
            type="text" 
            placeholder="Search (/ to focus)" 
            className="w-full border rounded p-1 text-sm"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="flex-1 overflow-y-auto" role="list">
          {isLoading ? (
            <div className="p-4 text-center text-gray-500">Loading (Skeletons)...</div>
          ) : items.length === 0 ? (
            <EmptyState />
          ) : (
            items.map(item => (
              <button 
                key={item.id} 
                onClick={() => setSelectedId(item.id)}
                aria-selected={selectedId === item.id}
                className={`w-full text-left p-4 border-b border-[#e5e7eb] cursor-pointer hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2563eb] ${selectedId === item.id ? "bg-blue-50" : ""}`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className={`font-semibold ${item.unread ? "text-black" : "text-gray-600"}`}>{item.subject}</span>
                  <SlaBadge hours={parseInt(item.sla_deadline)} />
                </div>
                <div className="text-sm text-gray-500">{item.sender}</div>
              </button>
            ))
          )}
        </div>
      </div>
      
      <div className="flex-1 flex flex-col bg-white overflow-y-auto">
        {selectedId ? (
          <div className="p-6">
            <h1 className="text-xl font-bold mb-4">{items.find(i => i.id === selectedId)?.subject}</h1>
            <TriageCard item={items.find(i => i.id === selectedId)} />
            
            <div className="mt-8 border-t pt-4">
              <h3 className="mb-2 font-semibold">Action Bar</h3>
              <div className="flex gap-2">
                <button 
                  disabled={isOffline} 
                  onClick={() => handleAction("accept")}
                  className="bg-[#2563eb] text-white px-4 py-2 rounded focus:outline-none focus-visible:ring-2 disabled:opacity-50"
                >
                  Accept & Route (a)
                </button>
                <button 
                  disabled={isOffline} 
                  onClick={() => handleAction("flag_legal")}
                  className="border border-[#e5e7eb] px-4 py-2 rounded focus:outline-none focus-visible:ring-2 disabled:opacity-50"
                >
                  Flag Legal (f)
                </button>
              </div>
              {errorMsg && <div className="text-red-500 mt-2 text-sm">{errorMsg}</div>}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Select an email to view details
          </div>
        )}
      </div>
    </div>
  );
};
