import React from 'react';
import { Globe } from 'lucide-react';

export default function CommissionerLinks() {
  return (
    <div className="space-y-3 pt-4 border-t border-[#E5E7EB]">
      <div className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Commissioner Research Libraries</div>
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
        <a href="https://www.priv.gc.ca/en/opc-actions-and-decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-300 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>Federal (OPC) Actions</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://www.cai.gouv.qc.ca/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-300 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>Québec (CAI) Sanctions</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://www.oipc.bc.ca/rulings/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-300 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>BC (OIPC) Rulings</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://oipc.ab.ca/decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-300 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>Alberta (OIPC) Decisions</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://www.ipc.on.ca/en/decisions" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-300 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>Ontario (IPC) Orders</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://oipc.sk.ca/decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-300 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>Saskatchewan (OIPC)</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://oipc.novascotia.ca/decisions" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>Nova Scotia (OIPC)</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://www.oipc.nl.ca/reports/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 flex justify-between items-center text-gray-700 transition-all shadow-xs">
          <span>Newfoundland (OIPC)</span>
          <Globe size={11} className="text-blue-600" />
        </a>
        <a href="https://www.ombudsman.mb.ca/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 flex justify-between items-center text-gray-700 col-span-2 transition-all shadow-xs">
          <span>Manitoba Ombudsman Reports</span>
          <Globe size={11} className="text-blue-600" />
        </a>
      </div>
    </div>
  );
}
