\# SanctionSnitch

\*\*Deterministic 6-Lender Home-Loan Pre-Qualification Engine for Indian Real Estate Deals\*\*  

\*A product by \*\*REALEST — Finance, AI and Investments\*\*\*



SanctionSnitch evaluates a buyer's financial profile against six Indian home-loan lenders (\*\*HDFC, ICICI, Axis, Bajaj Housing Finance, LIC Housing Finance, and SBI\*\*) to determine who will finance the deal, the exact maximum sanction, the binding constraint, total cash required to close, and ranked fixes for any shortfall.



Real estate deals routinely die late at the financing stage after brokers, buyers, and sellers have already invested weeks of time. SanctionSnitch surfaces underwriting bottlenecks upfront before time is wasted.



> \*\*Sample Client Deliverable:\*\* \[View Sample One-Page PDF Report (`samples/sample\_client\_report.pdf`)](samples/sample\_client\_report.pdf)



\---



\## Core Capabilities



\* \*\*Inputs:\*\* Net monthly income, existing EMIs, age, employment type (`salaried`, `self\_employed`, or `professional`), property value, available own funds, and CIBIL score (if known).

\* \*\*Three-Ceiling Maximum Sanction:\*\* Computes three independent ceilings per lender and selects the lowest:

&#x20; 1. \*\*Income Ceiling (FOIR):\*\* Maximum loan supported by net monthly income after existing EMI obligations.

&#x20; 2. \*\*Property Ceiling (LTV Slab):\*\* Property-value-based Loan-to-Value cap across lender-specific price slabs.

&#x20; 3. \*\*Tenure Ceiling:\*\* Maximum tenure constrained by each lender's retirement-age cap.

\* \*\*Binding Constraint Identification:\*\* Identifies whether \*\*Income\*\*, \*\*LTV\*\*, or \*\*Tenure\*\* caps the loan (e.g., ₹1.5L monthly income on a ₹75L property caps at ₹60L via LTV, whereas ₹90K income on the same property caps at \~₹40.58L via income).

\* \*\*Lender-Specific Policy Logic:\*\*

&#x20; \* \*\*CIBIL Enforcement:\*\* Four-state logic—ICICI enforces a hard floor (decline), HDFC and Bajaj apply soft floors (caveat flag), Axis and LIC HFL have verified absence, and SBI's floor is treated as unpublished.

&#x20; \* \*\*LTV \& Rate Structures:\*\* Handles SBI's two-slab LTV structure vs. three-slab structures elsewhere, Bajaj's separate pricing for professionals, and strict retirement-age tenure compression (e.g., a 54-year-old salaried buyer gets 6 years at HDFC).

\* \*\*Cash-to-Close Breakdown:\*\* Calculates down payment, stamp duty, registration, and lender-specific processing fees.

\* \*\*Shortfall \& Ranked Fixes:\*\* Quantifies the exact rupee gap and ranks actionable remedies (extending tenure, closing an existing liability, or negotiating property price below an LTV slab boundary), showing rupee impact and `%` of gap closed.

\* \*\*Branded PDF Output:\*\* Generates a one-page \*\*REALEST\*\* PDF report containing the borrower snapshot, recommended lender, full 6-lender comparison table, and transparent policy risk flags.



\---



\## Architecture \& How It Was Built



1\. \*\*Deterministic Core First:\*\* Zero LLM involvement in the calculation layer. Every rupee figure traces back to sourced lender policy data and verified financial math.

2\. \*\*Sourced Lender Matrix (`lenders/\*.json`):\*\* Six structured JSON files researched prior to engine code. Every policy field is tagged with `\_source` and `\_confidence` (`verified`, `partial`, `stale`, `unknown`, `verified\_absence`), directly governing engine behavior.

3\. \*\*Core Math (`emi.py`):\*\* Pure module for EMI, inverse `max\_principal()`, FOIR, tenure, and cash-to-close calculations.

4\. \*\*Lender Engine (`lender\_engine.py`):\*\* Single unified reader normalizing multiple interest-rate formats and LTV slab shapes—failing loudly on unrecognized schemas rather than guessing.

5\. \*\*Shortfall, Fees \& Orchestration:\*\*

&#x20;  \* `fix\_engine.py` — Shortfall math and ranked fix simulations.

&#x20;  \* `processing\_fee.py` — Parses four fee schemas; returns `None` + a verification flag where fees are true ranges (e.g., Bajaj).

&#x20;  \* `run\_all\_lenders.py` \& `borrower\_input.py` — Live CLI validation and lender ranking (declines sorted to the bottom).

6\. \*\*AI Extraction with Deterministic Guardrail (`extract\_salary\_slip.py`):\*\* Uses the Anthropic Claude API to parse pasted salary slips into structured fields, followed by a deterministic check verifying `gross - deductions == net`. Mismatches force confidence to `low`, and human confirmation is mandatory before data reaches the engine.

7\. \*\*PDF Report Generator (`generate\_report.py`):\*\* Built with `ReportLab` to render the one-page client/broker comparison report.



\---



\## Project Structure



```text

realest/

├── lenders/                  # Sourced JSON policy files (HDFC, ICICI, Axis, Bajaj, LIC HFL, SBI)

├── samples/                  # Sample client-ready PDF report output

├── emi.py                    # Core financial math \& inverse principal formulas

├── lender\_engine.py          # Unified lender policy parser \& ceiling evaluator

├── fix\_engine.py             # Shortfall quantification \& ranked fix calculator

├── processing\_fee.py         # Multi-schema processing fee engine

├── borrower\_input.py         # Interactive CLI borrower profile collector

├── run\_all\_lenders.py        # Multi-lender runner \& ranking logic

├── extract\_salary\_slip.py    # Claude API salary slip parser + deterministic net check

├── generate\_report.py        # ReportLab one-page PDF report generator

├── requirements.txt          # Python dependencies (reportlab, anthropic)

└── test\_\*.py                 # 6-file unit, regression, and 16-case edge test suite

