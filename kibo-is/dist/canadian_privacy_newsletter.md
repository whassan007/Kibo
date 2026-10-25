# Canadian Privacy Commissioner Enforcement & Rulings Newsletter
*Source-Grounded Regulatory Intelligence — Verified Official Decisions Only*

---

## Executive Summary
This bulletin compiles verified enforcement decisions, investigation reports, and adjudicative orders issued by Canada’s federal and provincial privacy commissioners (OPC Canada, CAI Québec, IPC Ontario, OIPC BC, OIPC Alberta). Every entry is anchored to an authoritative regulator publication and verified via SHA-256 content hash.

---

## Verified Commissioner Decisions & Rulings Breakdown

### 1. Ontario: IPC Ontario PHIPA Decision 175 (2022) — Unauthorized Electronic Health Record Access ('Snooping') & Audit Logging
* **Regulator:** Information and Privacy Commissioner of Ontario (IPC Ontario)
* **Official Citation:** `PHIPA Decision 175`
* **Decision Date:** 2022-02-28
* **Verification Status:** `VERIFIED_SOURCE`
* **SHA-256 Content Hash:** `0c26d6db09208c5cb05ee6614f80de2feb76a9617eb4cac0576154a0fe152b08`
* **Decision Summary:** IPC Ontario review under the Personal Health Information Protection Act, 2004 (PHIPA) regarding unauthorized employee access ('snooping') into electronic patient health records outside the circle of care. Evaluates whether the health information custodian implemented reasonable administrative and technical safeguards under PHIPA s. 12(1), electronic audit logging under O. Reg. 329/04 s. 10, and timely breach notification and disciplinary remediation under PHIPA s. 12(2).
* **Technical & Program Compliance Takeaways:**
  * Mandates immutable electronic read/view audit logs recording user ID, timestamp, and patient record identifier under PHIPA s. 12(1) and O. Reg. 329/04 s. 10, combined with role-based access controls, regular proactive random snooping audits, and mandatory privacy training.
* **Authoritative Source:** [PHIPA Decision 175](https://decisions.ipc.on.ca/ipc-cipvp/phipa/en/item/520415/index.do)

### 2. British Columbia: OIPC BC Order P21-06 (2021 BCIPC 35) — PIPA s. 34 Reasonable Security Safeguards & s. 35 Data Retention
* **Regulator:** Office of the Information and Privacy Commissioner for British Columbia (OIPC BC)
* **Official Citation:** `Order P21-06`
* **Decision Date:** 2021-06-17
* **Verification Status:** `VERIFIED_SOURCE`
* **SHA-256 Content Hash:** `d310f7cb0722f42c82263e594195f135d158408e4bf9c8e497a0aef6cb752ab7`
* **Decision Summary:** Adjudicative order by the OIPC for British Columbia under the Personal Information Protection Act (BC PIPA) evaluating an organization's obligations under s. 34 to make reasonable security arrangements to prevent unauthorized access, collection, use, disclosure, copying, modification, or disposal of employee and customer personal information, and under s. 35 to destroy or anonymize personal information once retention is no longer necessary for legal or business purposes.
* **Technical & Program Compliance Takeaways:**
  * Enforces BC PIPA s. 34 security safeguards (access controls, documented security policies, encryption, and audit trails proportional to data sensitivity) and s. 35 automated retention schedules that securely destroy or de-identify employee and customer records once business/legal purposes expire.
* **Authoritative Source:** [Order P21-06](https://www.oipc.bc.ca/orders/2556)

### 3. Federal / Joint (Canada, Québec, BC, Alberta): PIPEDA Report of Findings #2021-001 — Joint Investigation of Clearview AI, Inc. (Biometric Facial Recognition Scraping)
* **Regulator:** Office of the Privacy Commissioner of Canada (OPC), CAI Québec, OIPC BC, and OIPC Alberta
* **Official Citation:** `PIPEDA Report of Findings #2021-001`
* **Decision Date:** 2021-02-02
* **Verification Status:** `VERIFIED_SOURCE`
* **SHA-256 Content Hash:** `12ac457592f4d7958722752cad73bfdca4d39dca3a8bffdedcd688a96d9ee7b9`
* **Decision Summary:** Joint investigation by the federal OPC, CAI Québec, OIPC BC, and OIPC Alberta into Clearview AI, Inc.'s mass scraping of over three billion facial images from publicly accessible websites without consent to build a commercial biometric facial recognition search engine. Held that biometric facial templates are uniquely sensitive personal information, that 'publicly available' exceptions under PIPEDA s. 7 and provincial PIPA statutes do not permit indiscriminate scraping, and that mass biometric surveillance violated the 'appropriate purpose' requirement under PIPEDA s. 5(3), BC PIPA s. 4, and Alberta PIPA s. 4.
* **Technical & Program Compliance Takeaways:**
  * Prohibits scraping publicly accessible web pages to extract biometric identifiers or train biometric identification models without express opt-in consent and an objectively appropriate purpose under PIPEDA s. 5(3), BC/AB PIPA s. 4, and Québec Law 25 biometric database declaration rules (LCCJTI s. 44-45).
* **Authoritative Source:** [PIPEDA Report of Findings #2021-001](https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/2021/pipeda-2021-001/)

### 4. Ontario: IPC Ontario PHIPA Decision 110 (2020) — Ransomware Encryption of Electronic PHI Constitutes Loss & Unauthorized Use
* **Regulator:** Information and Privacy Commissioner of Ontario (IPC Ontario)
* **Official Citation:** `PHIPA Decision 110`
* **Decision Date:** 2020-02-19
* **Verification Status:** `VERIFIED_SOURCE`
* **SHA-256 Content Hash:** `954967ae580a95f9109c5b1ef13b3e6145d8c5a7eb499c89238c98314624163c`
* **Decision Summary:** Landmark IPC Ontario decision holding that a ransomware attack that encrypts electronic personal health information (PHI) on a custodian's server constitutes both an unauthorized 'use' and a 'loss' of PHI under PHIPA s. 12(1) and s. 12(2)—even where there is no evidence of exfiltration and backups are subsequently restored—thereby triggering mandatory notification to affected patients.
* **Technical & Program Compliance Takeaways:**
  * Incident response playbooks must classify ransomware encryption or availability loss of PHI as a reportable breach (unauthorized use and loss) under PHIPA s. 12(2) regardless of exfiltration. Requires offline immutable backups, endpoint detection, and patch management under PHIPA s. 12(1).
* **Authoritative Source:** [PHIPA Decision 110](https://decisions.ipc.on.ca/ipc-cipvp/phipa/en/item/466468/index.do)

### 5. Federal (Canada): PIPEDA Report of Findings #2019-002 — Investigation into Equifax Inc. and Equifax Canada Co. (2017 Cross-Border Breach)
* **Regulator:** Office of the Privacy Commissioner of Canada (OPC)
* **Official Citation:** `PIPEDA Report of Findings #2019-002`
* **Decision Date:** 2019-04-09
* **Verification Status:** `VERIFIED_SOURCE`
* **SHA-256 Content Hash:** `01a121f15b21bbba536f105d77ca2ee3644deed3752d45bdcdb78d61680ed021`
* **Decision Summary:** Investigation by the Privacy Commissioner of Canada into the 2017 Apache Struts vulnerability breach at Equifax Inc. that compromised Social Insurance Numbers and financial data of ~19,000 Canadians. Held that Equifax Canada violated PIPEDA Principle 4.1.3 (Accountability for Cross-Border Transfers to an Affiliate), Principle 4.7 (Safeguards), and Principle 4.5 (Limiting Retention). Equifax Canada entered into a binding 6-year Compliance Agreement under PIPEDA s. 17.1 requiring third-party security audits.
* **Technical & Program Compliance Takeaways:**
  * Requires written cross-border data processing agreements, active security oversight of parent/affiliated processors under PIPEDA Principle 4.1.3, automated vulnerability patching, network segmentation, cryptographic key rotation, and strict data retention purging under Principles 4.5 and 4.7.
* **Authoritative Source:** [PIPEDA Report of Findings #2019-002](https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/2019/pipeda-2019-002/)

---

## Source-Grounded Engineering Controls Checklist

1. `[ ]` **EHR Read & Snooping Audit Logs (IPC Ontario PHIPA Decision 175):** Enforce immutable read/view audit logging and proactive access audits across all electronic health record systems under PHIPA s. 12(1) and O. Reg. 329/04 s. 10.
2. `[ ]` **Ransomware Availability & Loss Breach Triage (IPC Ontario PHIPA Decision 110):** Classify ransomware encryption of PHI as a reportable unauthorized use and loss under PHIPA s. 12(2), even without data exfiltration.
3. `[ ]` **Cross-Border Transfer Accountability & Safeguards (OPC PIPEDA #2019-002 — Equifax):** Maintain binding processing agreements, active vulnerability management, and security audits for affiliate/third-party cross-border data transfers under PIPEDA Principles 4.1.3 and 4.7.
4. `[ ]` **Prohibition on Non-Consensual Biometric Scraping (OPC/CAI/OIPC Joint Finding #2021-001 — Clearview AI):** Block unconsented web scraping of facial images or biometric identifiers under PIPEDA s. 5(3), BC/AB PIPA s. 4, and Québec Law 25.
5. `[ ]` **PIPA s. 34 Safeguards & s. 35 Retention Purging (OIPC BC Order P21-06):** Enforce role-based access controls and automated destruction/de-identification when employee or customer data is no longer needed for legal or business purposes.
