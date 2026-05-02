# open-dd-agent 🔍

**An AI agent that automatically generates legal risk DD reports from official EDINET data — just by entering a company name**

[![Built with OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-red?style=flat-square)](https://openclaw.ai)
[![Powered by ISEAI](https://img.shields.io/badge/Powered%20by-ISEAI-blue?style=flat-square)](https://iseai.jp)
[![Data Source](https://img.shields.io/badge/Data-EDINET%20API%20v2-green?style=flat-square)](https://disclosure.edinet-fsa.go.jp)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## Overview

`open-dd-agent` is an AI agent that automates legal risk due diligence (DD) for listed companies.

Simply send a company name on Discord. The agent fetches and analyzes the latest annual securities report directly from the Financial Services Agency's official database **EDINET API v2**, then generates a legal risk report based on disclosure requirements under the **Financial Instruments and Exchange Act (FIEA)** and the **Cabinet Office Ordinance on Disclosure of Corporate Information**.

```
Discord: /dd Toyota Motor

→ Fetching annual securities report from EDINET... (docID: S100XXXX)
→ Analyzing "Business Risks" section...
→ 📋 LegalDD Report — Toyota Motor Corporation (7203)
   ...
```

---

## Demo

> **Submitted product for Clawathon Tokyo Edition (May 2, 2026)**

| Command | Description |
|---------|-------------|
| `/dd [company name]` | Generate a legal risk DD report |
| `/dd [company name] --type legal` | Legal risks only (default) |
| `/dd help` | Show help |

### Sample Output

```markdown
## 📋 LegalDD Report — HODL1 Co., Ltd. (3719)
**Analysis Date**: May 2, 2026 15:32
**Data Source**: EDINET Annual Securities Report (30th fiscal year, docID: S100XXXXX)

### Overall Risk Summary
| Category                        | Risk Level  | Summary                                              |
|---------------------------------|-------------|------------------------------------------------------|
| Going Concern                   | 🔴 High     | Material going concern events noted                  |
| Litigation / Legal Disputes     | 🔴 High     | Ongoing lawsuits totaling over ¥3.3 billion          |
| Regulation / Licensing          | 🟡 Medium   | Risk of regulatory changes for crypto asset exchange |
| Compliance / Misconduct         | 🔴 High     | Misconduct by former management confirmed in report  |
| Governance                      | 🔴 High     | Full management turnover in 2025                     |
| Material Contracts              | 🟡 Medium   | Multiple contracts related to datio in solutum       |
| IP / Information Security       | 🟢 Low      | No notable risk disclosures                          |
| Finance / Funding (Legal)       | 🔴 High     | Dilution risk from third-party allotment warrants    |

⚠️ This report is an automated AI analysis of publicly available EDINET information.
It does not constitute legal advice. Please consult qualified professionals for legal or investment decisions.
```

---

## Architecture

```
Discord
   │  /dd [company name]
   ▼
ISEAI Gateway (OpenClaw on Alibaba Cloud)
   │
   ├─ [General Assistant]         Company name interpretation & legal risk analysis
   ├─ [Programming Agent]         Executes edinet_fetcher.py
   └─ [Office Assistant]          Markdown report formatting & output
          │
          ▼
   EDINET API v2 (Financial Services Agency)
   https://api.edinet-fsa.go.jp/api/v2/
   │
   ├─ Document List API  → Retrieve docID of latest annual securities report
   └─ Document Fetch API → PDF download → Extract "Business Risks" section
```

---

## Legal Basis

The DD framework in this product is based on the following laws and standards.

| Law / Standard | Reference | Mapping to DD Framework |
|----------------|-----------|------------------------|
| Financial Instruments and Exchange Act (FIEA), Article 24 | Obligation to submit annual securities reports | Basis for selecting target documents |
| Cabinet Office Ordinance on Corporate Disclosure, Form 2 | "Business Risks" disclosure requirement | Design basis for the 8-category DD framework |
| Cabinet Office Ordinance on Corporate Disclosure, Form 2 | "Material Contracts" disclosure requirement | Basis for Category 6 (Material Contracts Risk) |
| Auditing Standards Committee Report 570 | Going concern assumption | Basis for Category 1 (Going Concern Risk) |

---

## Legal Risk DD Categories (Phase 1 MVP)

The following 8 categories are defined as the standard DD framework, based on typical disclosure elements required by FIEA and the Cabinet Office Ordinance under "Business Risks."

| # | Category | Key Review Items |
|---|----------|-----------------|
| 1 | **Going Concern (GC Risk)** | Presence of GC notes, 3-year P&L trend, GC doubt disclosures |
| 2 | **Litigation / Legal Disputes** | Overview and claim amounts of pending lawsuits, administrative penalties |
| 3 | **Regulation / Licensing** | Status of required licenses and registrations, regulatory change risks |
| 4 | **Compliance / Misconduct** | Scandals or accounting fraud, whistleblower system, anti-social forces |
| 5 | **Governance** | Board independence, sudden management changes, director litigation |
| 6 | **Material Contracts** | Concentration/dependency on key contracts, CoC clauses, related-party transactions |
| 7 | **IP / Information Security** | Patent/trademark infringement risk, cybersecurity incidents |
| 8 | **Finance / Funding (Legal Aspects)** | Financial covenants, third-party allotment appropriateness, dilution disclosures |

---

## Setup

### Prerequisites

- [ISEAI](https://iseai.jp/) account (OpenClaw managed service)
- Discord account and server
- [EDINET API v2](https://api.edinet-fsa.go.jp/) Subscription-Key

### 1. Obtain EDINET API Key

Issued immediately with just an email address at the [EDINET API Application Page](https://api.edinet-fsa.go.jp/api/auth/index.aspx?mode=1).

### 2. Configure ISEAI

1. Sign in to [ISEAI](https://iseai.jp/) and open your workspace
2. Add `EDINET_API_KEY` to environment variables
3. Upload `scripts/edinet_fetcher.py` to the workspace
4. Paste the contents of `SOUL.md` into the agent configuration

### 3. Set Up Discord Bot

1. Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications)
2. Issue a Bot Token from the Bot tab
3. Paste the Token into the ISEAI Discord settings screen
4. Invite the Bot to your server using the OAuth2 URL Generator
5. Send `hello` via Discord DM to confirm pairing

### 4. Verify Operation

Run the following on Discord to confirm it works:

```
/dd Toyota Motor
```

---

## File Structure

```
open-dd-agent/
├── README.md                    # This file (Japanese)
├── README.en.md                 # This file (English)
├── SOUL.md                      # Agent personality & behavioral guidelines
├── AGENTS.md                    # Multi-agent configuration
├── scripts/
│   ├── edinet_fetcher.py        # EDINET API call & PDF analysis core
│   └── requirements.txt         # Dependency libraries
├── prompts/
│   ├── system_prompt.md         # Main system prompt
│   ├── legal_risk_v1.md         # Phase 1 legal risk analysis prompt
│   └── full_dd_v1.md            # Phase 2 full DD (planned)
├── examples/
│   ├── demo_input.md            # Demo input samples
│   └── demo_output.md           # Demo output samples
└── docs/
    ├── architecture.md          # System architecture details
    ├── legal_basis.md           # FIEA & Cabinet Office Ordinance legal basis
    ├── dd_categories.md         # DD category definitions and rationale
    └── roadmap.md               # Phase 1–3 roadmap
```

---

## Roadmap

```
Phase 1 (MVP)  ← Current
  Company name input → EDINET API → Legal risk 8-category DD report
  Discord integration

Phase 2 (Next Development)
  Add A-2 type: high-accuracy analysis via document text paste
  Integration of XBRL/CSV (type=5) structured financial data
  Expand to full DD covering finance, governance, and more

Phase 3 (Future Vision)
  Real-time monitoring of timely disclosures with automatic alerts
  Cross-company comparative analysis
  TDnet integration
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Platform | [ISEAI](https://iseai.jp/) (OpenClaw on Alibaba Cloud) |
| Channel | Discord |
| Data Source | EDINET API v2 (Financial Services Agency) |
| PDF Parsing | pdfplumber |
| Language | Python 3.11+ |

---

## Disclaimer

Reports generated by this product are automated AI analyses of publicly available EDINET information and **do not constitute legal advice, investment recommendations, or any other professional counsel**. For final decisions on legal or investment matters, please consult qualified professionals.

---

## License

MIT License — See [LICENSE](LICENSE) for details.
