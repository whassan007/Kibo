/**
 * KIBO Privacy OS — Multilingual UI Localization & Legal Text Integrity (Agent G16)
 * Supports English (`en`), French (`fr` - Canada / EU), and German (`de` - EU / DACH).
 * Crucial Legal Rule: Official legal citations and statutory quotes remain in their
 * authoritative source language unless accompanied by an explicitly labeled translation note.
 */

export type SupportedLocale = 'en' | 'fr' | 'de';

export interface UiTranslations {
  skipToMain: string;
  brandTitle: string;
  brandSubtitle: string;
  commandPaletteHint: string;
  nav: {
    home: string;
    inbox: string;
    assessments: string;
    incidents: string;
    rights: string;
    dataVendors: string;
    regulatory: string;
    risksControls: string;
    reports: string;
    assistant: string;
    admin: string;
  };
  metrics: {
    overdue: string;
    needApproval: string;
    openIncidents: string;
    regulatoryChanges: string;
  };
  actions: {
    runEvaluation: string;
    saveDraft: string;
    submitForApproval: string;
    approve: string;
    requestChanges: string;
    escalateCounsel: string;
    exportAuditBundle: string;
  };
  legalIntegrityBanner: string;
}

export const TRANSLATIONS: Record<SupportedLocale, UiTranslations> = {
  en: {
    skipToMain: 'Skip to main workspace content',
    brandTitle: 'KIBO Privacy OS',
    brandSubtitle: 'Multi-Jurisdictional Enterprise Privacy Office System of Record (US · Canada · EU)',
    commandPaletteHint: 'Search or jump (⌘K / Ctrl+K)',
    nav: {
      home: 'Home',
      inbox: 'Inbox',
      assessments: 'Assessments',
      incidents: 'Incidents',
      rights: 'Privacy Rights',
      dataVendors: 'Data & Vendors',
      regulatory: 'Regulatory Intelligence',
      risksControls: 'Risks & Controls',
      reports: 'Reports',
      assistant: 'Assistant',
      admin: 'Administration',
    },
    metrics: {
      overdue: 'Overdue Deadlines',
      needApproval: 'Need Approval',
      openIncidents: 'Open Incidents',
      regulatoryChanges: 'Verified Regulatory Updates',
    },
    actions: {
      runEvaluation: 'Evaluate Jurisdictional Applicability',
      saveDraft: 'Save Draft',
      submitForApproval: 'Submit for Governance Approval',
      approve: 'Approve with Audit Signature',
      requestChanges: 'Request Changes',
      escalateCounsel: 'Escalate to Privacy Counsel',
      exportAuditBundle: 'Export SHA-256 Sealed Evidence Pack',
    },
    legalIntegrityBanner:
      'Authoritative statutory citations (USC, CFR, L.R.Q. c. P-39.1, EU CELEX, BDSG, CNIL) are preserved verbatim in their official source language.',
  },
  fr: {
    skipToMain: 'Passer au contenu principal de l’espace de travail',
    brandTitle: 'KIBO Privacy OS',
    brandSubtitle: 'Système de référence du bureau de la protection des renseignements personnels (É.-U. · Canada · UE)',
    commandPaletteHint: 'Rechercher ou naviguer (⌘K / Ctrl+K)',
    nav: {
      home: 'Accueil',
      inbox: 'Boîte de réception',
      assessments: 'Évaluations (EFVP / AIPD)',
      incidents: 'Incidents',
      rights: 'Droits des personnes',
      dataVendors: 'Données et fournisseurs',
      regulatory: 'Veille réglementaire',
      risksControls: 'Risques et contrôles',
      reports: 'Rapports',
      assistant: 'Assistant gouverné',
      admin: 'Administration',
    },
    metrics: {
      overdue: 'Échéances dépassées',
      needApproval: 'En attente d’approbation',
      openIncidents: 'Incidents actifs',
      regulatoryChanges: 'Mises à jour réglementaires vérifiées',
    },
    actions: {
      runEvaluation: 'Évaluer l’applicabilité juridictionnelle',
      saveDraft: 'Enregistrer le brouillon',
      submitForApproval: 'Soumettre pour approbation',
      approve: 'Approuver avec signature d’audit',
      requestChanges: 'Demander des modifications',
      escalateCounsel: 'Transmettre au conseiller juridique',
      exportAuditBundle: 'Exporter le dossier de preuve scellé SHA-256',
    },
    legalIntegrityBanner:
      'Les références législatives officielles (Loi 25 du Québec, LPRPDE/PIPEDA, RGPD CELEX, USC) sont conservées intégralement dans leur langue officielle d’origine.',
  },
  de: {
    skipToMain: 'Zum Hauptinhalt des Datenschutz-Arbeitsbereichs springen',
    brandTitle: 'KIBO Privacy OS',
    brandSubtitle: 'Mandantenfähiges Datenschutz-Managementsystem (USA · Kanada · Europäische Union)',
    commandPaletteHint: 'Suchen oder springen (⌘K / Ctrl+K)',
    nav: {
      home: 'Startseite',
      inbox: 'Posteingang',
      assessments: 'Folgenabschätzungen (DSFA)',
      incidents: 'Vorfälle & Meldepflichten',
      rights: 'Betroffenenrechte (DSAR)',
      dataVendors: 'Verarbeitungsverzeichnis & Auftragsverarbeiter',
      regulatory: 'Regulatorische Intelligenz',
      risksControls: 'Risiken & TOM-Kontrollen',
      reports: 'Berichte & Nachweise',
      assistant: 'Gesteuerter KI-Assistent',
      admin: 'Administration',
    },
    metrics: {
      overdue: 'Überfällige Fristen',
      needApproval: 'Freigabe erforderlich',
      openIncidents: 'Offene Sicherheitsvorfälle',
      regulatoryChanges: 'Geprüfte Rechtsänderungen',
    },
    actions: {
      runEvaluation: 'Rechtsanwendbarkeit prüfen (JRAE)',
      saveDraft: 'Entwurf speichern',
      submitForApproval: 'Zur DSB-/Rechtsfreigabe einreichen',
      approve: 'Mit Audit-Signatur freigeben',
      requestChanges: 'Änderungen anfordern',
      escalateCounsel: 'An Datenschutzjustiziar eskalieren',
      exportAuditBundle: 'SHA-256-versiegeltes Nachweispaket exportieren',
    },
    legalIntegrityBanner:
      'Amtliche Gesetzeszitate (DSGVO, BDSG, TDDDG, Québec Law 25, US-Recht) bleiben unverändert in ihrer authentischen Originalsprache erhalten.',
  },
};

export function formatAuthoritativeCitation(
  citation: string,
  originalLanguage: 'en' | 'fr' | 'de' = 'en',
  activeLocale: SupportedLocale = 'en'
): { verbatimCitation: string; languageTag: string; isOriginalLanguage: boolean } {
  return {
    verbatimCitation: citation,
    languageTag: originalLanguage.toUpperCase(),
    isOriginalLanguage: originalLanguage === activeLocale,
  };
}
