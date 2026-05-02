# Requirements Definition Document (RDD) v2.0
## LegalDD Agent — Automated Legal Risk DD Report Generator for Listed Companies

**Version**: 2.0
**Created**: May 2, 2026
**Hackathon**: Clawathon Tokyo Edition (Next AI Leaders)
**Target Awards**: ISEAI Prize (¥100,000), Grand Prize (¥125,000)

---

## 1. Project Overview

### 1.1 Product Name
**LegalDD Agent**

### 1.2 One-line Description
An AI agent that accepts a listed company name via Discord, directly retrieves the annual securities report from the EDINET API, and **automatically generates a legal risk DD report** based on disclosure requirements under the Financial Instruments and Exchange Act (FIEA) and the Cabinet Office Ordinance on Corporate Disclosure.

### 1.3 Background & Problem

In M&A, investment, and legal review workflows, initial legal risk screening of a target company requires lawyers and analysts to read across multiple disclosure documents. This process is highly formulaic and well-suited to automation by an AI agent.

Existing Legal AI products are predominantly document-paste type (A-2 type). There is a clear gap in the market for **A-1 type systems that autonomously retrieve and structure data from official government databases (EDINET) using only a company name**.

### 1.4 Differentiation Axes

| Axis | Details |
|------|---------|
| Data source accuracy | Retrieves original annual securities reports directly from EDINET API (official FSA source), not web search |
| Explicit legal basis | Uses FIEA Article 24 and Cabinet Office Ordinance Form 2 disclosure items as the DD framework |
| Ease of use | Enter only a company name — powered by ISEAI (OpenClaw) + Discord integration |
| Extensible design | Clear roadmap from Phase 1 (legal risks) → Phase 2 (full DD including finance, governance, etc.) |

---

## 2. Scope Definition

### 2.1 Phase Structure

```
Phase 1 (Hackathon MVP)
  Input:  A-1 type — company name only
  Source: EDINET API v2 (annual securities report PDF)
  Output: Legal risk 8-category DD report
  Channel: Discord

Phase 2 (Post-hackathon)
  Input:  A-2 type added — also accepts document text paste
  Source: EDINET API XBRL/CSV (type=5) structured financial data
  Output: Expanded to full DD covering finance, governance, and more
```

### 2.2 Target Companies
All companies listed on the Tokyo Stock Exchange that have submitted annual securities reports to EDINET.

---

## 3. Functional Requirements

### 3.1 Discord Command Specification

```
/dd [company name]
```

**Examples:**
```
/dd Toyota Motor
/dd Mercari, Inc.
/dd HODL1
```

**Options:**
```
/dd [company name] --type legal     # Legal risks only (default)
/dd help                            # Show command help
```

**Design Principles:**
- Natural language input (e.g., "Check the legal risks of [company]") works equivalently
- If the company is not found in EDINET, respond to Discord accordingly
- Send progress messages during processing ("Fetching...", "Analyzing...")

### 3.2 Agent Processing Flow

```
[Discord] /dd [company name]
    │
    ▼
[Step 1] Company Identification
  Look up the company name in the EDINET code list (CSV)
  to obtain the EDINET code (Exxxxx)
    │
    ▼
[Step 2] Retrieve docID (Document List API)
  GET https://api.edinet-fsa.go.jp/api/v2/documents.json
    ?date={most recent business day}
    &type=2
    &Subscription-Key={EDINET_API_KEY}
  → Filter by ordinanceCode="010" & formCode="030000"
  → Get the latest annual securities report docID for the target company
    │
    ▼
[Step 3] Fetch Document (Document Fetch API)
  GET https://api.edinet-fsa.go.jp/api/v2/documents/{docID}
    ?type=2
    &Subscription-Key={EDINET_API_KEY}
  → ZIP → Extract PDF
  → Extract "Business Risks" section using pdfplumber
    │
    ▼
[Step 4] Legal Risk Analysis
  Classify extracted text into 8 categories
  Evaluate severity (High/Medium/Low) for each category
    │
    ▼
[Step 5] Report Generation & Discord Output
  Output in Markdown format
  Append source URL and disclaimer
```

### 3.3 Non-Functional Requirements

| Item | Requirement |
|------|-------------|
| Response time | Initial response within 60 seconds of command input |
| Output language | Japanese (report content) |
| Data source | EDINET API v2 (annual securities report, type=2) |
| Disclaimer | Always append a statement that the output is not legal advice |
| Error handling | Notify Discord on company identification failure or API failure |

---

## 4. Output Specification

### 4.1 Legal Risk DD Report Structure (Phase 1 MVP)

Based on the "Business Risks" disclosure requirements of FIEA Article 24 and Cabinet Office Ordinance Form 2, the following 8 categories are defined as the standard DD framework. HODL1 Co., Ltd. (E05320, filing dated April 30, 2026) is used as a reference example to derive general elements.

#### DD Category Definitions

| # | Category | Disclosure Basis | Key Review Items |
|---|----------|-----------------|-----------------|
| 1 | Going Concern (GC Risk) | Cabinet Office Ordinance Form 2 / Auditing Standards Committee Report 570 | Presence of GC notes, 3-year P&L trend, GC doubt disclosures |
| 2 | Litigation / Legal Disputes | Cabinet Office Ordinance Form 2 "Business Risks" | Overview and claim amounts of pending lawsuits, administrative penalties, impact of litigation costs on financials |
| 3 | Regulation / Licensing | Cabinet Office Ordinance Form 2 "Business Risks" | Status of required licenses and registrations, regulatory change risks, industry-specific regulatory environment |
| 4 | Compliance / Misconduct | Cabinet Office Ordinance Form 2 / CG Report | Scandals or accounting fraud, whistleblower system, anti-social forces exclusion |
| 5 | Governance | Cabinet Office Ordinance Form 2 / CG Report (TSE requirement) | Board independence, sudden management changes, director litigation, conflicts with controlling shareholders |
| 6 | Material Contracts | Cabinet Office Ordinance Form 2 "Material Contracts" | Concentration/dependency on key contracts, termination/CoC clauses, related-party transactions |
| 7 | IP / Information Security | Cabinet Office Ordinance Form 2 "Business Risks" | Patent/trademark infringement risk, Personal Information Protection Act compliance, cybersecurity incidents |
| 8 | Finance / Funding (Legal Aspects) | Cabinet Office Ordinance Form 2 "Business Risks" | Financial covenants, appropriateness of third-party allotments, dilution disclosures |

### 4.2 Discord Output Format

```markdown
## 📋 LegalDD Report — [Company Name] (Securities Code: XXXX)
**Analysis Date**: YYYY-MM-DD HH:MM
**Data Source**: EDINET Annual Securities Report (docID: XXXXXXXX)

---

### Overall Risk Summary
| Category                    | Risk Level  | Summary |
|-----------------------------|-------------|---------|
| Going Concern               | 🔴 High     | Material going concern events noted |
| Litigation / Legal Disputes | 🔴 High     | Ongoing lawsuits totaling ¥3.3 billion |
| Regulation / Licensing      | 🟡 Medium   | Risk of regulatory changes for crypto asset exchange |
| Compliance                  | 🔴 High     | Misconduct by former management confirmed in investigation report |
| Governance                  | 🔴 High     | Full management turnover in 2025; hollow board structure confirmed |
| Material Contracts          | 🟡 Medium   | Multiple contracts related to datio in solutum |
| IP / Information Security   | 🟢 Low      | No notable risk disclosures |
| Finance / Funding (Legal)   | 🔴 High     | Dilution risk from third-party allotment warrants |

---

### Detailed Analysis

#### 1. Going Concern (GC Risk) 🔴 High
[3–5 line description with evidence extracted from EDINET source text]

#### 2. Litigation / Legal Disputes 🔴 High
[3–5 line description with evidence extracted from EDINET source text]

(Continued for each category)

---

### Data Sources
- EDINET: https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?...
- Document: Annual Securities Report (30th fiscal year, FY ended October 2025)

---
⚠️ This report is an automated AI analysis of publicly available EDINET information.
It does not constitute legal advice. Please consult qualified professionals for legal or investment decisions.
```

---

## 5. Technical Design

### 5.1 System Architecture

```
[Discord] ───────────────────────────────────────────────┐
    │                                                    │
    ▼                                                    │
[ISEAI Gateway]                                          │
  (OpenClaw on Alibaba Cloud)                            │
    │                                                    │
    ├──[General Assistant]──────────────────────────────┤
    │     Company name interpretation, analysis logic    │
    │                                                    │
    ├──[Programming Agent]──────────────────────────────┤
    │     Executes edinet_fetcher.py                     │
    │     EDINET API calls & PDF parsing                 │
    │                                                    │
    └──[Office Assistant]───────────────────────────────┘
          Markdown report formatting

[External APIs]
  ├── EDINET API v2 (Financial Services Agency)
  │     https://api.edinet-fsa.go.jp/api/v2/
  └── EDINET Code List CSV (FSA public download)
        https://disclosure2dl.edinet-fsa.go.jp/...
```

### 5.2 EDINET API v2 Specification Details

#### Endpoint List

| API | Endpoint | Purpose |
|-----|----------|---------|
| Document List API | `GET /api/v2/documents.json` | Get docID list by date and document type |
| Document Fetch API | `GET /api/v2/documents/{docID}` | Download the document body as a ZIP |

#### Document Type Codes (used in this project)

| ordinanceCode | formCode | Document Type |
|--------------|----------|--------------|
| 010 | 030000 | Annual Securities Report |
| 010 | 030001 | Amended Annual Securities Report |
| 010 | 050000 | Securities Registration Statement (standard method) |

#### type Parameter (Document Fetch API)

| type value | Content | Phase 1 Usage |
|------------|---------|--------------|
| 2 | PDF | Main (extract "Business Risks" section) |
| 5 | XBRL/CSV | Phase 2 (structured financial data) |

#### Authentication

```
Subscription-Key: {EDINET_API_KEY}
※ Set via environment variable EDINET_API_KEY
```

### 5.3 edinet_fetcher.py Design

```python
"""
edinet_fetcher.py
Fetches the "Business Risks" section from annual securities reports using EDINET API v2.
"""
import requests, zipfile, io, os, json, sys, time
from datetime import datetime, timedelta
import pdfplumber

EDINET_API_KEY = os.environ.get("EDINET_API_KEY", "")
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"

# ------------------------------------------------------------------
# Step 1: Company Name → EDINET Code
# ------------------------------------------------------------------
def resolve_edinet_code(company_name: str) -> str | None:
    """
    Search for an EDINET code by company name in the EDINET code list CSV.
    Falls back from exact match to partial match.
    """
    url = ("https://disclosure2dl.edinet-fsa.go.jp/guide/static/"
           "disclosure/download/EKW0EAP0015.zip")
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        return None
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        csv_file = [f for f in z.namelist() if f.endswith(".csv")][0]
        content = z.read(csv_file).decode("cp932", errors="replace")
    for line in content.splitlines():
        cols = line.split(",")
        if len(cols) < 6:
            continue
        edinet_code = cols[0].strip().strip('"')
        name = cols[2].strip().strip('"')   # Submitter name
        if company_name in name or name in company_name:
            return edinet_code
    return None

# ------------------------------------------------------------------
# Step 2: EDINET Code → Latest Annual Securities Report docID
# ------------------------------------------------------------------
def get_latest_doc_id(edinet_code: str) -> tuple[str | None, str | None]:
    """
    Search back up to 365 days to find the latest annual securities report docID.
    Returns: (docID, submitDateTime)
    """
    for delta in range(0, 365):
        date = (datetime.today() - timedelta(days=delta)).strftime("%Y-%m-%d")
        try:
            resp = requests.get(
                f"{BASE_URL}/documents.json",
                params={"date": date, "type": 2,
                        "Subscription-Key": EDINET_API_KEY},
                timeout=10
            )
            if resp.status_code != 200:
                continue
            for doc in resp.json().get("results", []):
                if (doc.get("edinetCode") == edinet_code
                        and doc.get("ordinanceCode") == "010"
                        and doc.get("formCode") == "030000"):
                    return doc["docID"], doc.get("submitDateTime", "")
            time.sleep(0.3)   # API rate limit handling
        except Exception:
            continue
    return None, None

# ------------------------------------------------------------------
# Step 3: docID → Extract "Business Risks" Text
# ------------------------------------------------------------------
def fetch_risk_section(doc_id: str) -> str:
    """
    Fetches the annual securities report PDF from EDINET and extracts the "Business Risks" section.
    """
    resp = requests.get(
        f"{BASE_URL}/documents/{doc_id}",
        params={"type": 2, "Subscription-Key": EDINET_API_KEY},
        timeout=60
    )
    if resp.status_code != 200:
        return f"[ERROR] Document fetch failed: HTTP {resp.status_code}"
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        pdf_files = [
            f for f in z.namelist()
            if f.endswith(".pdf") and "AuditDoc" not in f
        ]
        if not pdf_files:
            return "[ERROR] No PDF file found"
        pdf_bytes = z.read(pdf_files[0])
    risk_pages = []
    in_risk = False
    RISK_START = "事業等のリスク"      # "Business Risks" section header
    RISK_END   = "経営者による財政状態" # Next section header
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if RISK_START in text:
                in_risk = True
            if in_risk:
                risk_pages.append(text)
            if in_risk and RISK_END in text:
                break
    return "\n".join(risk_pages) if risk_pages else "[INFO] Risk section not found"

# ------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------
def run(company_name: str) -> dict:
    result = {"company": company_name, "edinet_code": None,
              "doc_id": None, "submit_date": None, "risk_text": ""}
    edinet_code = resolve_edinet_code(company_name)
    if not edinet_code:
        result["error"] = f"Company '{company_name}' not found in EDINET code list"
        return result
    result["edinet_code"] = edinet_code
    doc_id, submit_date = get_latest_doc_id(edinet_code)
    if not doc_id:
        result["error"] = "Annual securities report not found (searched past 365 days)"
        return result
    result["doc_id"] = doc_id
    result["submit_date"] = submit_date
    result["risk_text"] = fetch_risk_section(doc_id)
    return result

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "Toyota Motor"
    output = run(company)
    print(json.dumps(output, ensure_ascii=False, indent=2))
```

### 5.4 Prompt Design (SOUL.md)

```markdown
# LegalDD Agent

## Role
You are a legal risk analysis agent named LegalDD.
You receive listed company names via Discord, retrieve annual securities reports
directly from the EDINET API, and generate legal risk DD reports based on FIEA
and Cabinet Office Ordinance disclosure requirements.

## /dd Command Processing Steps

1. Run edinet_fetcher.py to retrieve the "Business Risks" text from the annual securities report:
   ```
   python edinet_fetcher.py "[company name]"
   ```

2. Analyze the retrieved text across the following 8 categories:
   - Going Concern (GC Risk)
   - Litigation / Legal Disputes
   - Regulation / Licensing
   - Compliance / Misconduct
   - Governance
   - Material Contracts
   - IP / Information Security
   - Finance / Funding (Legal Aspects)

3. Assign a risk rating (🔴 High / 🟡 Medium / 🟢 Low) to each category.
   Rating criteria:
   - High: Risks that could materially impact financial results or business continuity are explicitly stated
   - Medium: Risks exist but are currently limited or managed
   - Low: No notable risk disclosures, or disclosure is at a general level

4. Output in the specified Markdown format to Discord

## Prohibited Actions
- Including investment recommendations or buy/sell recommendations
- Making definitive statements about unverified facts
- Assessments without cited sources

## Required Disclaimer
Always append the following at the end of every report:
"⚠️ This report is an automated AI analysis of publicly available EDINET information.
It does not constitute legal advice. Please consult qualified professionals for legal or investment decisions."
```

### 5.5 ISEAI Setup Instructions

#### Environment Variable Configuration
ISEAI Dashboard → Settings → Environment Variables — add the following:
```
EDINET_API_KEY=<your Subscription-Key>
```

#### Skill Deployment
1. Upload `edinet_fetcher.py` to the ISEAI Workspace
2. Confirm dependency libraries are installed: `requests`, `pdfplumber`

#### Discord Integration Setup
1. Discord Developer Portal → New Application → Create Bot
2. Obtain Bot Token → Paste into ISEAI Discord settings screen
3. Invite Bot to server using OAuth2 URL
4. Send a test DM to confirm pairing

---

## 6. Extension Roadmap

### Phase 1 (Hackathon MVP)
- A-1 type: Company name → EDINET API → Legal risk 8-category DD report
- Discord integration

### Phase 2 (Post-hackathon)

**Add A-2 type:**
```
/dd upload [company name]
→ Agent waits for document text paste
→ High-accuracy analysis combining EDINET data with pasted document
```

**Financial data integration via XBRL/CSV (type=5):**
- Direct parsing of XBRL elements such as `jpcorp_cor:NetSalesSummary`
- 5-year trend analysis of financial indicators
- Visualization of revenue, profit, cash flow, and net assets over time

**Output category expansion:**

| Additional Category | Corresponding EDINET Disclosure Item |
|---------------------|--------------------------------------|
| Financial Status | Summary of key management indicators |
| Business Environment Risks | Market, competition, technology changes |
| Governance Details | Corporate governance report |
| Shareholders / Control | Major shareholders, conflicts with controlling shareholders |
| Sustainability | ESG / climate change risk disclosures |

### Phase 3 (Future Vision)
- Periodic monitoring (auto-alert on timely disclosures)
- Cross-company comparative analysis
- TDnet real-time integration

---

## 7. GitHub Submission Specification

### 7.1 Repository Structure

```
legaldd-agent/
├── README.md                    # Project overview, demo, setup (Japanese)
├── README.en.md                 # Project overview, demo, setup (English)
├── SOUL.md                      # Agent personality & behavioral guidelines
├── AGENTS.md                    # Multi-agent configuration
├── scripts/
│   ├── edinet_fetcher.py        # EDINET API call & PDF analysis core
│   └── requirements.txt         # Dependencies (requests, pdfplumber)
├── prompts/
│   ├── system_prompt.md         # Main system prompt
│   ├── legal_risk_v1.md         # Phase 1 legal risk analysis prompt
│   └── full_dd_v1.md            # Phase 2 full DD (placeholder)
├── examples/
│   ├── demo_input.md            # Demo input samples (multiple companies)
│   └── demo_output.md           # Demo output samples (actual generated results)
└── docs/
    ├── architecture.md          # System architecture diagram
    ├── legal_basis.md           # FIEA & Cabinet Office Ordinance legal basis
    ├── dd_categories.md         # DD category definitions and rationale
    └── roadmap.md               # Phase 1–3 roadmap
```

### 7.2 Git Commit Plan (for development history 30% criteria)

```
commit 1  [~12:30]  init: project structure and README skeleton
commit 2  [~13:00]  feat: add SOUL.md and agent configuration
commit 3  [~13:30]  feat: add edinet_fetcher.py core script
commit 4  [~14:00]  feat: add legal risk prompt template
commit 5  [~15:30]  fix: refine prompt based on first EDINET test
commit 6  [~16:30]  test: add demo output for HODL1 and second company
commit 7  [~17:00]  docs: add architecture diagram and legal basis
commit 8  [~17:30]  feat: add Discord command documentation
commit 9  [~18:00]  chore: finalize README and submission materials
```

### 7.3 Akindo Submission Contents
1. Product name: LegalDD Agent
2. Target sponsor award: ISEAI Prize
3. GitHub repository URL
4. Demo video or screenshots (Discord operation scenes)
5. Explicit description of ISEAI usage
6. Tech stack: ISEAI (OpenClaw / Alibaba Cloud) + Discord + EDINET API v2

---

## 8. Demo Scenario (for 18:10 submission deadline)

### 8.1 Demo Flow (estimated 3-minute presentation)

**Step 1** Show the LegalDD Bot participating in a Discord server

**Step 2** Live input:
```
/dd HODL1 Co., Ltd.
```
→ "Fetching annual securities report from EDINET..." is displayed
→ Report output after 30–60 seconds

**Step 3** Compare with another company:
```
/dd Toyota Motor
```
→ Contrast with a case where risk is low

**Step 4** Presentation key points:
- "With just a company name, legal risks are structured from official EDINET data"
- "A DD framework grounded in FIEA and Cabinet Office Ordinance legal requirements"
- "Direct applicability to IPO/M&A practice at MHM"
- Phase 2/3 roadmap

### 8.2 Backup Plan
In case of EDINET API response delays, pre-save output samples for 2–3 companies in `examples/demo_output.md` to present in case of live failure.

---

## 9. Constraints & Risks

### 9.1 Technical Constraints

| Constraint | Details | Mitigation |
|------------|---------|-----------|
| ISEAI Python execution availability | Confirm at workshop (12:00) | Fall back to Web Fetch approach if unavailable |
| EDINET API rate limits | Daily limit exists (details unconfirmed) | Throttling via time.sleep(0.3) |
| PDF parsing accuracy | pdfplumber reliably gets full text, but section boundary detection depends on PDF structure | Pre-verify with manual samples |
| Response time | PDF fetch and parsing may exceed 60 seconds | Handle with progress messages |

### 9.2 Legal Considerations
- Always include a statement that the output is not legal advice
- Always note that use for investment decisions is not recommended
- Always note that generative AI output may contain inaccuracies

---

## 10. Disclaimer

Reports generated by this product are automated AI analyses of publicly available EDINET information and do not constitute legal advice, investment recommendations, or any other professional counsel. For final decisions on legal or investment matters, please consult qualified professionals.
