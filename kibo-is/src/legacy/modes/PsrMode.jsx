import React from 'react';
import { ShieldAlert, BookOpen, Terminal, Clock, Users } from 'lucide-react';
import CommissionerLinks from '../components/CommissionerLinks';

const PsrMode = ({
  psrMeetings, psrRiskQueue, psrSelectedRisk, setPsrSelectedRisk,
  psrVote, setPsrVote, psrRecommendation, setPsrRecommendation,
  handlePsrRecommendationSubmit, psrTransitionTasks,
  psrCopilotQuery, setPsrCopilotQuery, psrCopilotAnswer, setPsrCopilotAnswer
}) => {
  const nextMeeting = psrMeetings[0];
  const pendingVotes = psrRiskQueue.filter(r => r.status === 'pending').length;

  const sortedQueue = [...psrRiskQueue].sort((a, b) => {
    if (a.status === 'pending' && b.status !== 'pending') return -1;
    if (b.status === 'pending' && a.status !== 'pending') return 1;
    return 0;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50/50 p-6 space-y-6">
      
      {/* Hero Band (P0-1) */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-6 rounded-xl shadow-xs mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="k-title text-xl font-bold text-white">Next PSR Committee Meeting</h1>
            {nextMeeting ? (
              <>
                <p className="k-body mt-1 text-blue-100 uppercase tracking-wider font-bold">
                  {nextMeeting.type.replace('_', ' ')}
                </p>
                <p className="k-body mt-2 text-white">
                  Agenda: {nextMeeting.agenda.join(' | ')}
                </p>
              </>
            ) : (
              <p className="k-body mt-1 text-blue-100">No upcoming meetings scheduled.</p>
            )}
          </div>
          <div className="flex items-center gap-4 bg-white/10 rounded-xl px-5 py-4 backdrop-blur-sm border border-white/20 shadow-xs">
            <Clock className="w-6 h-6 text-blue-100" />
            <div className="flex flex-col">
              <span className="k-metric font-bold text-2xl text-white leading-none">{pendingVotes}</span>
              <span className="k-body text-blue-100 uppercase tracking-wider font-bold mt-1">Waiting on your vote</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top row: Side-by-side panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        
        {/* Left Column: Meetings & Materials */}
        <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-6 shadow-xs">
          
          <div className="space-y-3">
            <div className="k-eyebrow uppercase tracking-wider text-gray-800">All Scheduled Meetings</div>
            <div className="space-y-2.5">
              {psrMeetings.map(m => (
                <div key={m.meeting_id} className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-2 shadow-xs">
                  <div className="flex justify-between items-center">
                    <span className="k-body font-bold text-gray-900">Meeting ID: {m.meeting_id}</span>
                    <span className="text-blue-600 uppercase k-eyebrow font-bold">{m.type.replace('_', ' ')}</span>
                  </div>
                  <div className="k-body text-gray-700 leading-relaxed">Agenda: {m.agenda.join(' | ')}</div>
                  {m.minutes ? (
                    <div className="k-body text-gray-700 bg-gray-50 p-3.5 rounded-lg border border-[#E5E7EB] mt-1">
                      Minutes: {m.minutes}
                    </div>
                  ) : (
                    <div className="k-body text-gray-400 italic">Minutes pending recording by CPO</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Materials */}
          <div className="space-y-3 pt-4 border-t border-[#E5E7EB]">
            <div className="k-eyebrow uppercase tracking-wider text-gray-500">Advisory Review Materials</div>
            <div className="grid grid-cols-1 gap-2.5">
              <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl flex justify-between items-center shadow-xs">
                <span className="k-body font-bold text-[#111827]">Quebec Law 25 Diagnostic Posture.pdf</span>
                <button className="text-blue-600 k-eyebrow font-bold uppercase border border-[#E5E7EB] hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs">Download</button>
              </div>
              <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl flex justify-between items-center shadow-xs">
                <span className="k-body font-bold text-[#111827]">Cross-Border Transfer TIA v1.docx</span>
                <button className="text-blue-600 k-eyebrow font-bold uppercase border border-[#E5E7EB] hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs">Download</button>
              </div>
              <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl flex justify-between items-center shadow-xs">
                <span className="k-body font-bold text-[#111827]">Privacy Commissioner Rulings (July 2026).md</span>
                <a href="/canadian_privacy_newsletter.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 k-eyebrow font-bold uppercase border border-[#E5E7EB] hover:bg-gray-50 px-3 py-1.5 rounded-lg text-center transition-all shadow-xs">View</a>
              </div>
            </div>
          </div>

          {/* Research & Regulatory Libraries */}
          <CommissionerLinks />

        </div>

        {/* Right Column: Risk Advisory Queue */}
        <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-6 shadow-xs">
          
          <div className="space-y-3">
            <div className="k-eyebrow uppercase tracking-wider text-gray-800">Risk Advisory Queue</div>
            <div className="space-y-4">
              {sortedQueue.map(risk => {
                const isSelected = psrSelectedRisk?.risk_id === risk.risk_id;
                return (
                <div
                  key={risk.risk_id}
                  className={`rounded-xl border transition-all bg-white shadow-xs overflow-hidden ${
                    isSelected ? 'border-blue-500 ring-1 ring-blue-500' : 'border-[#E5E7EB] hover:border-gray-300'
                  }`}
                >
                  <div 
                    onClick={() => setPsrSelectedRisk(risk)}
                    className="p-4 cursor-pointer space-y-3"
                  >
                    <div className="flex justify-between items-center">
                      <span className="k-title font-bold text-gray-900">{risk.issue.substring(0, 40)}...</span>
                      {risk.status === 'pending' ? (
                        <span className="k-eyebrow bg-rose-100 text-rose-800 px-2 py-1 rounded-md font-bold uppercase">Needs your vote</span>
                      ) : (
                        <span className="k-eyebrow bg-gray-100 text-gray-600 px-2 py-1 rounded-md font-bold uppercase">Closed</span>
                      )}
                    </div>
                    <div className="k-body text-[#111827] leading-relaxed">{risk.issue}</div>
                    
                    {/* Details Disclosure */}
                    <details className="k-body text-gray-500 mt-2">
                      <summary className="cursor-pointer hover:text-gray-700 font-semibold">View Meta Details</summary>
                      <div className="pt-2 pl-2 border-l-2 border-gray-200 mt-2 space-y-1">
                        <div><span className="font-semibold text-gray-700">Risk ID:</span> {risk.risk_id}</div>
                        <div><span className="font-semibold text-gray-700">Status:</span> {risk.status}</div>
                      </div>
                    </details>

                    {risk.recommendations && risk.recommendations.length > 0 && (
                      <div className="border-t border-[#E5E7EB] pt-3 mt-3 space-y-2">
                        <div className="k-eyebrow font-semibold text-gray-500 uppercase">Committee Consensus:</div>
                        <div className="space-y-2">
                          {risk.recommendations.map((r, i) => (
                            <div key={i} className="flex items-start gap-2 bg-gray-50 p-2 rounded-lg border border-gray-100">
                              <span className={`k-eyebrow px-2 py-1 rounded-md text-white font-bold uppercase shrink-0 ${
                                r.vote === 'approve' ? 'bg-emerald-600' :
                                r.vote === 'conditional' ? 'bg-amber-600' : 'bg-rose-600'
                              }`}>
                                {r.vote}
                              </span>
                              <div className="k-body text-gray-800">
                                <span className="font-bold text-gray-900">{r.member}:</span> "{r.recommendation}"
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Inline Voting Form */}
                  {isSelected && risk.status === 'pending' && (
                    <div className="bg-blue-50/50 border-t border-blue-100 p-4 space-y-4">
                      <div className="k-eyebrow font-bold uppercase tracking-wider text-[#111827]">Submit Recommendation</div>
                      <form onSubmit={handlePsrRecommendationSubmit} className="space-y-4">
                        <div>
                          <label className="block k-eyebrow text-gray-700 font-semibold uppercase mb-1">Advisory Vote</label>
                          <select 
                            value={psrVote}
                            onChange={(e) => setPsrVote(e.target.value)}
                            className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 k-body text-[#111827] rounded-lg cursor-pointer transition-all shadow-xs"
                          >
                            <option value="approve">Approve (Operational clearance)</option>
                            <option value="conditional">Conditional Approval (Mitigation required)</option>
                            <option value="reject">Reject (Action needed)</option>
                          </select>
                        </div>

                        <div>
                          <label className="block k-eyebrow text-gray-700 font-semibold uppercase mb-1">Detailed Recommendation Notes</label>
                          <textarea 
                            required
                            value={psrRecommendation}
                            onChange={(e) => setPsrRecommendation(e.target.value)}
                            placeholder="Provide detailed compliance guidance for the CPO..."
                            className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-3 k-body text-[#111827] rounded-lg h-24 resize-none transition-all shadow-xs"
                          />
                        </div>

                        <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 k-body tracking-wide rounded-lg shadow-sm transition-all cursor-pointer">
                          Submit Recommendation
                        </button>
                      </form>
                    </div>
                  )}

                </div>
              )})}
            </div>
          </div>
        </div>

      </div>

      {/* Bottom Row: Dynamic Notes-derived Tracker Cockpit (Full Width) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Gen AI Procurement Gateways & Revocation */}
        <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs lg:col-span-1">
          <h3 className="k-eyebrow font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-1.5">
            <ShieldAlert size={16} className="text-indigo-650" />
            <span>Gen AI Procurement & IP Security Gates</span>
          </h3>
          <p className="k-body text-gray-500 leading-relaxed">
            Innovative Procurement Model (Ontario approved): Sequential gates mapping the transition from Nascent to OpenText/Cohere technical builds.
          </p>
          <div className="space-y-3">
            <div className="p-3 bg-indigo-50/15 border border-indigo-200 rounded-xl space-y-2">
              <div className="flex justify-between items-center k-eyebrow font-bold">
                <span className="text-indigo-900 uppercase">Nascent Access Revocation</span>
                <span className="text-emerald-700 bg-emerald-50 border border-emerald-250 px-2 py-0.5 rounded">Verified</span>
              </div>
              <p className="k-body text-gray-600">Neil & Bryan confirmed in writing that all IP, keys, and database credentials have been fully revoked from the previous developer.</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between k-body font-semibold text-gray-655">
                <span>Innovative Procurement Progression</span>
                <span className="text-blue-655 font-bold">Stage 1 of 3</span>
              </div>
              <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden border border-gray-200">
                <div className="bg-blue-600 h-full w-[33.3%]" />
              </div>
              <div className="grid grid-cols-3 k-eyebrow text-gray-400 font-bold uppercase pt-1 text-center">
                <span className="text-blue-700">LOI (June 8)</span>
                <span>MOU (Build Plan)</span>
                <span>DPA (Contract)</span>
              </div>
            </div>
          </div>
        </div>

        {/* PSR Advisory Tasks List */}
        <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs lg:col-span-1">
          <h3 className="k-eyebrow font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-1.5">
            <BookOpen size={16} className="text-blue-600" />
            <span>PSR Advisory Action Registry</span>
          </h3>
          <p className="k-body text-gray-500">Action items assigned during May 27 & Oct 8 committee meetings.</p>
          <div className="space-y-3 max-h-[260px] overflow-y-auto pr-1">
            {psrTransitionTasks.map(t => (
              <div key={t.id} className="p-4 bg-gray-50 border border-gray-200 rounded-xl space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-gray-900 k-body">{t.title}</span>
                  <span className={`px-2 py-1 rounded k-eyebrow font-bold uppercase ${
                    t.status === 'completed' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-amber-50 text-amber-800 border border-amber-200'
                  }`}>
                    {t.status}
                  </span>
                </div>
                <p className="k-body text-gray-600 leading-relaxed">{t.notes}</p>
                <div className="flex justify-between items-center k-eyebrow text-gray-500 pt-2 border-t border-gray-150">
                  <span>Owner: <code className="bg-gray-100 px-1 rounded font-bold">{t.owner}</code></span>
                  <span>ID: {t.id}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Copilot FAQ Audit Tool */}
        <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs lg:col-span-1">
          <h3 className="k-eyebrow font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-1.5">
            <Terminal size={16} className="text-indigo-650" />
            <span>SharePoint Copilot FAQ Auditer</span>
          </h3>
          <p className="k-body text-gray-500">
            Audit AI responses to secure SharePoint directories before wide staff rollout.
          </p>
          <div className="space-y-3">
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="Ask PSR Copilot (e.g. when to contact PSR...)"
                value={psrCopilotQuery}
                onChange={(e) => setPsrCopilotQuery(e.target.value)}
                className="flex-1 bg-white border border-gray-300 rounded-lg p-2.5 k-body focus:ring-1 focus:ring-blue-500 focus:outline-hidden"
              />
              <button 
                onClick={() => {
                  if (psrCopilotQuery.toLowerCase().includes('when')) {
                    setPsrCopilotAnswer("PSR Copilot: Staff should contact the PSR Committee when starting any new technical project processing personal info, initiating SaaS vendor onboarding, or if a potential confidentiality incident or PHI breach is suspected.");
                  } else if (psrCopilotQuery.toLowerCase().includes('breach')) {
                    setPsrCopilotAnswer("PSR Copilot: SUSPECTED BREACH PROTOCOL: Revoke credentials immediately to contain access. Conduct RROSH risk screening. Log details in the internal confidentiality incident register. Alert the OPC/IPC and affected individuals at first reasonable opportunity.");
                  } else {
                    setPsrCopilotAnswer("PSR Copilot: Request parsed. Response generated from verified SharePoint compliance directory (ver. 1.04).");
                  }
                }}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-4 py-2 rounded-lg k-body transition-all cursor-pointer shadow-xs"
              >
                Audit
              </button>
            </div>
            {psrCopilotAnswer && (
              <div className="p-3 bg-gray-50 text-indigo-900 k-body rounded-lg border border-indigo-100 leading-relaxed max-h-[120px] overflow-y-auto font-medium">
                {psrCopilotAnswer}
              </div>
            )}
            <div className="k-eyebrow text-gray-400 italic">
              Note: A strict disclaimer message will accompany all staff-facing Copilot interfaces.
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default PsrMode;
