# SanctionSnitch
**Deterministic 6-Lender Home-Loan Pre-Qualification Engine for Indian Real Estate Deals**  
*A product by **REALEST — Finance, AI and Investments***

SanctionSnitch evaluates a buyer's financial profile against six Indian home-loan lenders (**HDFC, ICICI, Axis, Bajaj Housing Finance, LIC Housing Finance, and SBI**) to determine who will finance the deal, the exact maximum sanction, the binding constraint, total cash required to close, and ranked fixes for any shortfall.

Real estate deals routinely die late at the financing stage after brokers, buyers, and sellers have already invested weeks of time. SanctionSnitch surfaces underwriting bottlenecks upfront before time is wasted.

> **Sample Client Deliverable:** [View Sample One-Page PDF Report (`samples/sample_client_report.pdf`)](samples/sample_client_report.pdf)

---

## Core Capabilities

* **Inputs:** Net monthly income, existing EMIs, age, employment type (`salaried`, `self_employed`, or `professional`), property value, available own funds, and CIBIL score (if known).
* **Three-Ceiling Maximum Sanction:** Computes three independent ceilings per lender and selects the lowest:
  1. **Income Ceiling (FOIR):** Maximum loan supported by net monthly income after existing EMI obligations.
  2. **Property Ceiling (LTV Slab):** Property-value-based Loan-to-Value cap across lender-specific price slabs.
  3. **Tenure Ceiling:** Maximum tenure constrained by each lender's retirement-age cap.
* **Binding Constraint Identification:** Identifies whether **Income**, **LTV**, or **Tenure** caps the loan (e.g., ₹1.5L monthly income on a ₹75L property caps at ₹60L via LTV, whereas ₹90K income on the same property caps at ~₹40.58L via income).
* **Lender-Specific Policy Logic:**
  * **CIBIL Enforcement:** Four-state logic—ICICI enforces a hard floor (decline), HDFC and Bajaj apply soft floors (caveat flag), Axis and LIC HFL have verified absence, and SBI's floor is treated as unpublished.
  * **LTV & Rate Structures:** Handles SBI's two-slab LTV structure vs. three-slab structures elsewhere, Bajaj's separate pricing for professionals, and strict retirement-age tenure compression (e.g., a 54-year-old salaried buyer gets 6 years at HDFC).
* **Cash-to-Close Breakdown:** Calculates down payment, stamp duty, registration, and lender-specific processing fees.
* **Shortfall & Ranked Fixes:** Quantifies the exact rupee gap and ranks actionable remedies (extending tenure, closing an existing liability, or negotiating property price below an LTV slab boundary), showing rupee impact and `%` of gap closed.
* **Branded PDF Output:** Generates a one-page **REALEST** PDF report containing the borrower snapshot, recommended lender, full 6-lender comparison table, and transparent policy risk flags.

---

## Architecture & How It Was Built

1. **Deterministic Core First:** Zero LLM involvement in the calculation layer. Every rupee figure traces back to sourced lender policy data and verified financial math.
2. **Sourced Lender Matrix (`lenders/*.json`):** Six structured JSON files researched prior to engine code. Every policy field is tagged with `_source` and `_confidence` (`verified`, `partial`, `stale`, `unknown`, `verified_absence`), directly governing engine behavior.
3. **Core Math (`emi.py
