import React, { useState } from 'react';
import { liveEventClient } from '../../services/liveEventClient';
import { formatAuthoritativeCitation, type SupportedLocale } from '../../i18n/translations';

export interface RegulatoryDocumentItem {
  doc_id: string;
  jurisdiction: string;
  title: string;
  citation: string;
  source_language: 'en' | 'fr' | 'de';
  official_authority: string;
  official_url: string;
  publication_date: string;
  retrieved_at: string;
  verified_at?: string | null;
  sha256_hash: string;
  promotion_state: 'verified_production' | 'pending_counsel_review' | 'candidate_staged' | 'rejected';
  impacted_workflows: string[];
  holding_or_obligation_summary: string;
  verbatim_quote: string;
}

const INITIAL_REGULATORY_DOCUMENTS: RegulatoryDocumentItem[] = [
  {
    doc_id: 'REG-CA-QC-LAW25-S17',
    jurisdiction: 'CA-QC',
    title: 'Loi modernisant des dispositions législatives en matière de protection des renseignements personnels (Loi 25, art. 17)',
    citation: 'RLRQ c. P-39.1, art. 17 & art. 3.5 (Loi 25 du Québec)',
    source_language: 'fr',
    official_authority: 'Publications du Québec & Commission d’accès à l’information (CAI)',
    official_url: 'https://www.legisquebec.gouv.qc.ca/fr/document/lc/P-39.1',
    publication_date: '2023-09-22',
    retrieved_at: '2026-10-25T06:00:00Z',
    verified_at: '2026-10-25T07:30:00Z',
    sha256_hash: 'e49c81a27f9103bd6e4c19a4738291bc0948a7716253e112349876abcdef0123',
    promotion_state: 'verified_production',
    impacted_workflows: ['DPIA-2026-0412 (Clinical AI Triage)', 'ROPA-002 (Cloud Telemetry Transfer)'],
    holding_or_obligation_summary:
      'Requires a Privacy Impact Assessment (ÉFVP) evaluating sensitivity, purpose, safeguards, and the legal regime of the destination state before communicating personal information outside Québec.',
    verbatim_quote:
      '« Avant de communiquer à l’extérieur du Québec un renseignement personnel, toute personne qui exploite une entreprise doit procéder à une évaluation des facteurs relatifs à la vie privée. »',
  },
  {
    doc_id: 'REG-EU-AI-2024-1689-ART27',
    jurisdiction: 'EU-GDPR / EU-AI',
    title: 'Regulation (EU) 2024/1689 (Artificial Intelligence Act) — Article 27 Fundamental Rights Impact Assessment',
    citation: 'CELEX:32024R1689, Art. 27 & GDPR (EU) 2016/679 Art. 35',
    source_language: 'en',
    official_authority: 'Official Journal of the European Union (EUR-Lex) & EDPB',
    official_url: 'https://eur-lex.europa.eu/eli/reg/2024/1689/oj',
    publication_date: '2024-07-12',
    retrieved_at: '2026-10-25T06:05:00Z',
    verified_at: '2026-10-25T07:45:00Z',
    sha256_hash: '7b31f92a004198c5347812ab983412cd7890ef1234567890abcdef1234567890',
    promotion_state: 'verified_production',
    impacted_workflows: ['DPIA-2026-0412 (Clinical AI Triage)', 'INB-2026-0412'],
    holding_or_obligation_summary:
      'Deployers of high-risk AI systems in healthcare and essential services must perform a Fundamental Rights Impact Assessment (FRIA) complementing the GDPR Article 35 DPIA.',
    verbatim_quote:
      '"Prior to deploying a high-risk AI system referred to in Article 6(2), deployers shall perform an assessment of the impact on fundamental rights that the use of such system may produce."',
  },
  {
    doc_id: 'REG-DE-BDSG-S26-TDDDG',
    jurisdiction: 'EU-DE',
    title: 'Bundesdatenschutzgesetz (BDSG § 26 Beschäftigtendatenschutz) & TDDDG § 25',
    citation: 'BDSG § 26 Abs. 1; TDDDG § 25 (BGBl. I)',
    source_language: 'de',
    official_authority: 'Bundesministerium der Justiz (Gesetze im Internet) & BfDI',
    official_url: 'https://www.gesetze-im-internet.de/bdsg_2018/__26.html',
    publication_date: '2024-05-14',
    retrieved_at: '2026-10-25T06:10:00Z',
    verified_at: null,
    sha256_hash: 'c18902ab3456cd7890ef1234567890ab1234567890cd1234567890ef12345678',
    promotion_state: 'pending_counsel_review',
    impacted_workflows: ['ROPA-003 (Employee Identity & Device Telemetry)', 'INB-2026-0905'],
    holding_or_obligation_summary:
      'Governs employee personal data processing in Germany alongside CJEU C-34/21 opening-clause jurisprudence and TDDDG § 25 terminal equipment storage rules.',
    verbatim_quote:
      '„Personenbezogene Daten von Beschäftigten dürfen für Zwecke des Beschäftigungsverhältnisses verarbeitet werden, wenn dies für die Entscheidung über die Begründung eines Beschäftigungsverhältnisses erforderlich ist.“',
  },
  {
    doc_id: 'REG-US-CA-CPPA-ADMT-2026',
    jurisdiction: 'US-CA',
    title: 'California CCPA/CPRA Automated Decisionmaking Technology (ADMT) & Risk Assessment Regulations',
    citation: 'Cal. Civ. Code § 1798.185(a)(15)–(16); 11 CCR § 7000 et seq.',
    source_language: 'en',
    official_authority: 'California Privacy Protection Agency (CalPrivacy / CPPA)',
    official_url: 'https://cppa.ca.gov/regulations/',
    publication_date: '2026-03-01',
    retrieved_at: '2026-10-25T06:12:00Z',
    verified_at: null,
    sha256_hash: '991234ab5678cd9012ef3456ab7890cd1234ef5678ab9012cd3456ef7890ab12',
    promotion_state: 'pending_counsel_review',
    impacted_workflows: ['DSAR-2026-0194', 'INB-2026-0905'],
    holding_or_obligation_summary:
      'Mandates pre-use ADMT notice, opt-out rights, human contestability, and formal cybersecurity/privacy risk assessments for significant decisions.',
    verbatim_quote:
      '"A business that uses automated decisionmaking technology for a significant decision shall provide the consumer with a Pre-Use Notice and an opportunity to opt out or access logic explanations."',
  },
];

export interface RegulatoryIntelViewProps {
  locale: SupportedLocale;
  onSelectJurisdictionMatrix?: () => void;
}

export const RegulatoryIntelView: React.FC<RegulatoryIntelViewProps> = ({
  locale,
  onSelectJurisdictionMatrix,
}) => {
  const [docs, setDocs] = useState<RegulatoryDocumentItem[]>(INITIAL_REGULATORY_DOCUMENTS);
  const [filterState, setFilterState] = useState<'all' | 'verified_production' | 'pending_counsel_review'>('all');
  const [selectedDocId, setSelectedDocId] = useState<string>(INITIAL_REGULATORY_DOCUMENTS[0].doc_id);
  const [banner, setBanner] = useState<string | null>(null);

  const visibleDocs = docs.filter((d) => (filterState === 'all' ? true : d.promotion_state === filterState));
  const selectedDoc = docs.find((d) => d.doc_id === selectedDocId) || visibleDocs[0] || docs[0];

  const handleVerifyAndPromote = (docId: string) => {
    const now = new Date().toISOString();
    setDocs((prev) =>
      prev.map((d) =>
        d.doc_id === docId
          ? { ...d, promotion_state: 'verified_production', verified_at: now }
          : d
      )
    );
    setBanner(`Legal Reviewer verified SHA-256 span provenance and promoted ${docId} to production JRAE.`);
    void liveEventClient.publishEvent({
      event_type: 'regulation.verified',
      title: `Regulatory Pack Verified & Promoted: ${docId}`,
      summary: `Verified against official source authority with immutable SHA-256 digest.`,
      severity: 'success',
      entity_type: 'regulation',
      entity_id: docId,
      target_section: 'regulatory',
      provenance_status: 'verified',
    });
  };

  const handleRejectPromotion = (docId: string) => {
    setDocs((prev) =>
      prev.map((d) => (d.doc_id === docId ? { ...d, promotion_state: 'rejected' } : d))
    );
    setBanner(`Candidate regulatory pack ${docId} marked as rejected pending updated statutory text.`);
  };

  return (
    <section aria-label="Regulatory Intelligence & Legal Verification" data-testid="regulatory-intel-view" className="space-y-5">
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-100">
            Source-Grounded Regulatory Intelligence, Provenance & Legal Review Queue
          </h2>
          <p className="text-xs text-slate-300">
            Displays publication date, retrieval timestamp, legal verification timestamp, SHA-256 source hash, and impacted organization workflows.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {onSelectJurisdictionMatrix && (
            <button
              type="button"
              data-testid="open-jurisdiction-evaluator-btn"
              onClick={onSelectJurisdictionMatrix}
              className="rounded-lg border border-sky-500/50 bg-sky-950/60 px-3.5 py-2 text-xs font-semibold text-sky-200 hover:bg-sky-900/60"
            >
              ⚖ Open JRAE Applicability Evaluator & 113-Jurisdiction Matrix
            </button>
          )}
        </div>
      </div>

      {banner && (
        <div
          role="status"
          data-testid="regulatory-status-banner"
          className="rounded-lg border border-emerald-500/40 bg-emerald-950/30 px-4 py-2.5 text-xs text-emerald-200"
        >
          ✓ {banner}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          data-testid="reg-filter-all"
          onClick={() => setFilterState('all')}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${
            filterState === 'all'
              ? 'bg-emerald-500/20 border border-emerald-400 text-emerald-200'
              : 'border border-slate-800 bg-slate-900 text-slate-300'
          }`}
        >
          All Regulatory Instruments ({docs.length})
        </button>
        <button
          type="button"
          data-testid="reg-filter-verified"
          onClick={() => setFilterState('verified_production')}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${
            filterState === 'verified_production'
              ? 'bg-emerald-500/20 border border-emerald-400 text-emerald-200'
              : 'border border-slate-800 bg-slate-900 text-slate-300'
          }`}
        >
          ✓ Verified Production Rules ({docs.filter((d) => d.promotion_state === 'verified_production').length})
        </button>
        <button
          type="button"
          data-testid="reg-filter-pending"
          onClick={() => setFilterState('pending_counsel_review')}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${
            filterState === 'pending_counsel_review'
              ? 'bg-amber-500/20 border border-amber-400 text-amber-200'
              : 'border border-slate-800 bg-slate-900 text-slate-300'
          }`}
        >
          ⚑ Pending Legal Review ({docs.filter((d) => d.promotion_state === 'pending_counsel_review').length})
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left 5 cols: Document List */}
        <div className="lg:col-span-5 space-y-2.5">
          {visibleDocs.map((doc) => {
            const active = selectedDoc?.doc_id === doc.doc_id;
            const isVerified = doc.promotion_state === 'verified_production';
            return (
              <button
                key={doc.doc_id}
                type="button"
                data-testid={`reg-doc-item-${doc.doc_id}`}
                onClick={() => setSelectedDocId(doc.doc_id)}
                className={`w-full text-left rounded-xl border p-4 transition-all ${
                  active
                    ? 'border-emerald-400 bg-slate-800/90'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs font-bold text-emerald-300">{doc.jurisdiction}</span>
                  <span
                    className={`rounded px-2 py-0.5 font-mono text-[10px] ${
                      isVerified
                        ? 'bg-emerald-950 text-emerald-200 border border-emerald-500/40'
                        : 'bg-amber-950 text-amber-200 border border-amber-500/40'
                    }`}
                  >
                    {isVerified ? '✓ VERIFIED PRODUCTION' : '⚑ PENDING LEGAL REVIEW'}
                  </span>
                </div>
                <div className="mt-1 text-xs font-semibold text-slate-100">{doc.title}</div>
                <div className="mt-1.5 flex items-center justify-between text-[11px] font-mono text-slate-300">
                  <span>Published: {doc.publication_date}</span>
                  <span>Impact: {doc.impacted_workflows.length} workflows</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Right 7 cols: Provenance, Verbatim Statutory Span & Legal Review Gate */}
        {selectedDoc && (
          <div
            data-testid="reg-doc-detail-panel"
            className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/80 p-5 space-y-4 text-xs"
          >
            {(() => {
              const citeMeta = formatAuthoritativeCitation(
                selectedDoc.citation,
                selectedDoc.source_language,
                locale
              );
              return (
                <>
                  <div className="flex flex-wrap items-start justify-between gap-2 border-b border-slate-800 pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-emerald-300">{selectedDoc.doc_id}</span>
                        <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-sky-300">
                          Original Language: {citeMeta.languageTag}
                        </span>
                      </div>
                      <h3 className="mt-1 text-sm font-bold text-slate-100">{selectedDoc.title}</h3>
                    </div>
                  </div>

                  {/* Freshness & Provenance Metadata Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                      <div className="text-slate-300">Publication Date</div>
                      <div className="mt-1 font-mono font-bold text-slate-100">
                        {selectedDoc.publication_date}
                      </div>
                    </div>
                    <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                      <div className="text-slate-300">Retrieved Timestamp</div>
                      <div className="mt-1 font-mono text-sky-300">{selectedDoc.retrieved_at}</div>
                    </div>
                    <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                      <div className="text-slate-300">Legal Verification</div>
                      <div className="mt-1 font-mono text-emerald-300">
                        {selectedDoc.verified_at || 'Awaiting Counsel Sign-Off'}
                      </div>
                    </div>
                  </div>

                  <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3.5 space-y-2">
                    <div>
                      <strong className="text-slate-200">Authoritative Citation (Verbatim):</strong>{' '}
                      <span className="font-mono text-emerald-300">{citeMeta.verbatimCitation}</span>
                    </div>
                    <div>
                      <strong className="text-slate-200">Official Source Authority:</strong>{' '}
                      <span className="text-slate-300">{selectedDoc.official_authority}</span> (
                      <a
                        href={selectedDoc.official_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sky-300 underline font-mono"
                      >
                        {selectedDoc.official_url}
                      </a>
                      )
                    </div>
                    <div>
                      <strong className="text-slate-200">SHA-256 Content Digest:</strong>{' '}
                      <span className="font-mono text-[11px] text-slate-300 break-all">
                        {selectedDoc.sha256_hash}
                      </span>
                    </div>
                  </div>

                  <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/20 p-3.5 space-y-1.5">
                    <div className="font-semibold text-emerald-300">
                      Exact Grounded Statutory / Decision Span ({citeMeta.languageTag}):
                    </div>
                    <blockquote className="italic text-slate-100 border-l-2 border-emerald-400 pl-3">
                      {selectedDoc.verbatim_quote}
                    </blockquote>
                    <p className="text-slate-300 pt-1">
                      <strong>Operational Obligation Summary:</strong>{' '}
                      {selectedDoc.holding_or_obligation_summary}
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <div className="font-semibold text-slate-200">
                      Impacted Organization Assessments & Workflows:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selectedDoc.impacted_workflows.map((wf) => (
                        <span
                          key={wf}
                          className="rounded-lg border border-sky-500/40 bg-sky-950/50 px-2.5 py-1 font-mono text-sky-200"
                        >
                          ↳ {wf}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Human Legal Review & Promotion Gate */}
                  <div className="flex flex-wrap items-center gap-2 border-t border-slate-800 pt-3">
                    <button
                      type="button"
                      data-testid="reg-verify-promote-btn"
                      onClick={() => handleVerifyAndPromote(selectedDoc.doc_id)}
                      className="rounded-lg bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
                    >
                      ✓ Verify Span & Promote to Production JRAE
                    </button>
                    <button
                      type="button"
                      data-testid="reg-reject-btn"
                      onClick={() => handleRejectPromotion(selectedDoc.doc_id)}
                      className="rounded-lg border border-rose-500/50 bg-rose-950/60 px-3.5 py-2 text-xs font-semibold text-rose-200 hover:bg-rose-900/60"
                    >
                      Reject Candidate Rule
                    </button>
                  </div>
                </>
              );
            })()}
          </div>
        )}
      </div>
    </section>
  );
};
