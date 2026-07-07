import React from 'react';
import { Lock } from 'lucide-react';

const PublicMode = ({
  jurConfig, activeJurisdiction, widgetName, setWidgetName, widgetEmail, setWidgetEmail,
  widgetType, setWidgetType, widgetDesc, setWidgetDesc, isSystemOnline, handlePublicSubmit,
  widgetStatus, widgetTrackId, handleWidgetCheckStatus, widgetCheckId, setWidgetCheckId, widgetCheckResult,
  companyName = "Acme Corp", companyInitials = "AC"
}) => {
  return (
    <main className="flex-1 flex flex-col items-center justify-center p-8 bg-[#F9FAFB] overflow-y-auto">
      <div className="w-full max-w-2xl bg-white border border-[#E5E7EB] rounded-2xl p-8 shadow-xs space-y-6">
        
        <div className="border-b border-[#E5E7EB] pb-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 text-white flex items-center justify-center text-lg font-bold rounded-lg shadow-sm">
              {companyInitials}
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-widest font-semibold">{companyName}</div>
              <h1 className="text-xl font-extrabold text-[#111827] tracking-tight">Privacy request centre</h1>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-gray-400 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100">
            <Lock size={14} />
            <span className="text-xs font-medium uppercase tracking-wider">Secure</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Left side: Request Submission */}
          <div className="space-y-4">
            <div className="text-sm text-[#111827] font-semibold border-b border-[#E5E7EB] pb-2">
              What would you like to do?
            </div>
            
            <form onSubmit={handlePublicSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs text-gray-500 font-semibold uppercase mb-1">Your Full Name</label>
                <input 
                  type="text" 
                  required 
                  value={widgetName}
                  onChange={(e) => setWidgetName(e.target.value)}
                  className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 font-semibold uppercase mb-1">Email Address</label>
                <input 
                  type="email" 
                  required 
                  value={widgetEmail}
                  onChange={(e) => setWidgetEmail(e.target.value)}
                  className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                  placeholder="john@example.com"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 font-semibold uppercase mb-1">Type of Request</label>
                <select 
                  value={widgetType} 
                  onChange={(e) => setWidgetType(e.target.value)}
                  className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg transition-all cursor-pointer shadow-xs"
                >
                  <option value="access">Access Personal Data</option>
                  <option value="deletion">Delete Personal Data</option>
                  <option value="opt-out">Opt-out of Profiling</option>
                  <option value="correction">Correct Data</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 font-semibold uppercase mb-1">Anything you’d like to add? (optional)</label>
                <textarea 
                  value={widgetDesc}
                  onChange={(e) => setWidgetDesc(e.target.value)}
                  className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg h-20 resize-none transition-all shadow-xs" 
                  placeholder="Details..."
                />
              </div>
              <button 
                type="submit" 
                disabled={!isSystemOnline}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 text-xs tracking-wide rounded-lg shadow-sm transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSystemOnline ? `Submit Request` : "Offline - Submission Blocked"}
              </button>
            </form>

            {widgetStatus === 'success' && (
              <div aria-live="polite" className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 text-xs rounded-lg space-y-1">
                <div>✓ Request registered successfully.</div>
                <div className="font-bold font-mono">Your reference number: {widgetTrackId}</div>
              </div>
            )}
            {widgetStatus === 'error' && (
              <div aria-live="polite" className="bg-rose-50 border border-rose-200 text-rose-800 p-3 text-xs rounded-lg">
                ✕ Something went wrong submitting your request. Please try again.
              </div>
            )}
          </div>

          {/* Right side: Check Status & Info */}
          <div className="space-y-6">
            {/* 1. Request Status Tracker */}
            <div>
              <h3 className="text-sm font-bold border-b pb-2 mb-2 text-gray-700">Track Your Request Status</h3>
              <form onSubmit={handleWidgetCheckStatus} className="flex space-x-2">
                <input 
                  type="text" 
                  required 
                  value={widgetCheckId}
                  onChange={(e) => setWidgetCheckId(e.target.value)}
                  placeholder="Enter your reference number (e.g., REQ-A12B34)" 
                  className="flex-1 bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-sm text-[#111827] rounded-lg transition-all shadow-xs"
                />
                <button type="submit" disabled={!isSystemOnline} className="bg-white hover:bg-gray-100 text-gray-700 border border-[#E5E7EB] px-4 py-2 text-sm rounded-lg transition-all cursor-pointer shadow-xs disabled:opacity-50 disabled:cursor-not-allowed">
                  Check Status
                </button>
              </form>
            </div>

            {/* 2. Live Status Output (if available) */}
            {widgetCheckResult && (
              <div className="bg-blue-50 border border-[#E5E7EB] p-4 rounded-xl text-sm space-y-3">
                <h4 className="text-blue-800 font-bold uppercase tracking-wide">Status</h4>
                <div>Reference Number: <span className="text-gray-900 font-mono ml-2">{widgetCheckResult.id}</span></div>
                <div>Status: <span className="text-gray-900 font-medium ml-2">{widgetCheckResult.status}</span></div>
                <div>We'll respond by: <span className="text-gray-900 font-medium ml-2">{widgetCheckResult.deadline}</span></div>
              </div>
            )}

            {/* 3. What happens next (Replaced Regulatory Notice) */}
            <div className="border border-[#E5E7EB] p-4 bg-yellow-50/50 rounded-xl text-sm space-y-2">
              <h4 className="text-gray-900 font-bold uppercase tracking-wide mb-1">What happens next</h4>
              <p className="text-gray-700 leading-relaxed">Once we receive your request, we will verify your identity. Under the <strong className="font-semibold text-gray-900">{jurConfig.primary_statute}</strong> (overseen by the <strong className="font-semibold text-gray-900">{jurConfig.regulator}</strong>), we will respond within <strong className="font-semibold text-gray-900">{jurConfig.access_deadline_days} days</strong>.</p>
            </div>
          </div>

        </div>

      </div>
    </main>
  );
};

export default PublicMode;
