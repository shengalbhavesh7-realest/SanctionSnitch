\# Rejection \& Friction Catalogue

\# Every way a home-loan file dies EVEN WHEN the sanction math says the buyer qualifies.



\## Schema — every entry uses these columns:

\# category   : income-doc | employer | property | profile | credit

\# trigger    : the specific thing that causes the problem

\# lenders    : which lenders enforce it (name them, or ALL / VARIES)

\# severity   : Decline| Rate-Load | Conditional

\# remediable : Yes | No | Partial

\# remediation: what the buyer/broker can actually do about it

\# source     : where I learned it



\---



\## CORE PRINCIPLE (the spine of this whole catalogue)

Lender verification rests on BANK-STATEMENT GROUND TRUTH — the one document that can't be faked and overrides applicant self-disclosure.

Everything downstream is a variation on how much ground truth a file can show:

\- Salaried clean = full ground truth (salary credits, verifiable)

\- Self-employed = ground truth exists but complex (net profit + depreciation + remuneration, NOT turnover)

\- Cash-salary = NO ground truth = often fatal

\- Property/pincode kills = collateral-side risk, separate from income ground truth



\## Income Documents



\### Salaried

| document | what it proves | field to extract later | source |



| Last 3 month's salary slips | Current net monthly income for FOIR |

Net monthly salary, deductions, employer name | HDFC docs page |



| Last 6 month's bank statements | To verify if cash flow is stable enough to repay the loan | Salary credits, Existing Emi, Loan repayments, Credit card repayments, average monthly balance, cheque bounces, failed ECS, auto debits, overdraft, negative balance | HDFC docs page |



| Latest form-16 and IT returns | Annual income legitimacy — employer-certified, TDS-linked, hard to fake | Applicant name, Pan number, Employer name, Gross annual salary, Total taxable income, other/rental income, Financial year, TDS deducted, ITR filing status | HDFC docs page |



\### Self-Employed

| document | what it proves | field to extract later | source |



| ITR + computation of income (2yrs, CA-attested, individual + business) | Tax-declared income — the legal floor the lender computes on. You can't borrow against income you didn't file. | Gross professional/business receipts, business/professional expenses, net profit/professional income, depreciation, other income, gross total income, 80C and 80D deductions, Total taxable income | HDFC docs page |



| Balance sheet + P\&L (2 years, CA-attested, individual + business) | To evaluate the financial health, profitability and stability of the borrower's business | Net profit, Depreciation, Partner's remuneration | HDFC docs page |



| 12 months bank statements (business current A/C + individual savings A/C) | To verify the borrower's actual cash flow, income consistency, and repayment behavior | Actual cash flow, turnover, bounces, average balance | HDFC docs page |



\### CRITICAL RULE - self-employed income is NOT turnover

Eligibility income = Net Profit + Depreciation added back + Partner's Remuneration



* Depreciation added back because: it is a non-cash accounting expense—the business records it, but no cash actually leaves the business in that year.
* Partner's remuneration added back because: if the applicant is the partner, that remuneration is effectively their own income from the business, not an expense paid to an unrelated employee.
* Naive tools anchor on turnover and overstate eligibility massively
* Becomes engine function later: self\_employed\_income(net\_profit, depreciation, remuneration)



source: HDFC docs + domain knowledge



\## Employer Categories (Cat A/B/C)



\### Concept

An employer category is a lender’s internal risk label for your company, used to estimate job stability, salary reliability, and how easy it would be to verify and recover the loan.



\### Category breakdown

| category | typical employers | treatment | source |



| Cat A | Listed companies, top-tier corporates, large multinationals, government concerns, PSUs, and other “hot lead” employers in a lender’s approved list | lower rate, higher eligibility, lighter friction, faster approval | Money control, My money mantra(aggregator) |



| Cat B | Strong but not top-tier private companies, established firms, companies with decent turnover/growth, and some mid-tier employers in approved lists | Usually acceptable, but with more checks than Cat A | Money control, My money mantra(aggregator) |



| CAT C | Smaller, lower-ranked, unlisted, or less established employers; employers outside the bank’s preferred/approved list | May face rate-load, tighter FOIR/tenure, manual review, or decline | Money control, My money mantra(aggregator) |



\### As rejection/friction rows (schema format)

| category | trigger | lenders | severity | remediable | remediation | source |



| employer | Cat-C/unlisted employer | varies | Rate-Load/decline | Partial | Move to a lender whose approved-company list includes your employer, or apply through an NBFC with looser employer rules; improve salary stability and complete documentation | your loan advisors(aggregator)|



| employer | employer not in approved/tie-up list | varies | Decline/Delay | Partial | Ask for manual underwriting, provide salary slips, bank statements, employment proof, and HR confirmation; if the lender requires a list match, switch lenders | axis bank |



| employer | Lower-ranked employer profile | varies | Rate load/lower sanction | partial | Reduce FOIR, keep salary credits regular, show longer job tenure, and clean up bureau/profile issues before reapplying | axis bank |



GAP: No public source lists which specific companies fall in A/B/C — it's each lender's internal, proprietary list. Concept is public; the actual classification is not. This is the #1 thing to extract from a DSA.

GAP: No public source gives exact rate-loading in bps for Cat-C, or names which lenders are strictest/softest on employer category. Also DSA territory.



\### CONFIRMED FINDING

No universal Cat A/B/C list exists. Each lender classifies employers internally and differently — the same employer can be Cat A at one bank, Cat C at another. A broker cannot look this up; it's DSA/insider knowledge. This is the moat.



\### SOURCE CONFIDENCE (for the employer section above)

\- SBI homeloans page = lender-authoritative (trust most)

\- Moneycontrol = credible media (secondary)

\- LinkedIn / imimg = anecdotal (trust least, verify before use)

\- All rows gathered via Perplexity synthesis: concept is verified, exact per-lender classification is NOT — needs a DSA to confirm.



\## Property-Side Kills

(The buyer can be perfect - the PROPERTY is unlendable. Kills the deal for ALL buyers, not just one.)



| trigger | what it is / why it kills | lenders | severity | remediable | remediation | source |



| No OC (Occupancy Certificate) | An OC is proof that the building was completed as per approved plan and is fit for occupation; without it, the property may be treated as unauthorized, may not get basic utilities, and banks often do not prefer lending on it because it increases legal and resale risk. a no-OC flat also means the buyer can't get a clean resale later and may face penalties/regularization costs. | varies | Decline/Delay | Partial | If the property is under construction, OC may not yet be needed; for a ready property, ask the builder to obtain OC or avoid taking possession until it is issued. In some resale cases, lenders may proceed if there is a completion certificate, approved plan, tax receipts, and a satisfactory technical/legal audit | axis bank, livemint |



| Non-APF project(Approved project financing) | APF means the lender has already vetted the project’s legal, technical, and financial aspects; if a project is not on the lender’s APF list, the bank has to do fresh project-level due diligence, which slows processing and can trigger extra scrutiny or refusal if the project looks risky | varies | Delay, Rate-Load, Possible decline | Partial | Use a project already on the lender’s APF list, or have the broker check whether the chosen lender can add the project after due diligence | Bajajfinserv, brickplot |



| Title defect / unclear ownership | Lenders need clear title because the property is the collateral; if ownership, title deeds, encumbrances, or approvals are unclear, the bank may not be able to safely mortgage the asset | varies | Fatal/conditional | Partial | Resolve title issues first via legal review, chain-of-title checks, encumbrance verification, and correction of missing approvals or disputes before reapplying | Bajajfinserv, Brickplot |



| Agreement value > lender valuation | The lender uses its own property valuation for risk and LTV, so if the sale/agreement price is above that valuation, the bank will usually cap the loan on the lower lender valuation and require the buyer to fund the shortfall. This doesn’t always kill the deal, but it can make the transaction unaffordable or outside the borrower’s available down payment | varies | Conditional (cash gap) | Partial | increase down payment, renegotiate price, or proceed only if the borrower can cover the gap. If the gap is too large, the deal effectively dies for that buyer | brigadegroup,grihumhousing |



GAP notes

No OC: The sources clearly say banks often dislike non-OC ready properties, but they do not give a universal lender list of who will always refuse. OC strictness varies most across lenders — worth DSA confirmation on who funds no-OC ready flats.



Non-APF project: The sources explain what APF is and why it helps, but they do not provide a public universal list of lenders that are strict vs lenient on APF.



Title defect: The sources support the need for title vetting, but they do not give one public standardized “fatal title defect” checklist across lenders.



Valuation gap: The sources support the principle that loan terms depend on appraisal/valuation, but they do not spell out every bank’s exact sanction formula.



\## Negative Profiles

(Buyer perfect on income/employer/property/CIBIL - still declined for WHO or WHERE they are. Most lender-specific, least documented.)



| trigger | why it's a red flag | lenders | severity | remediable | remediation | source |



| Negative pincode/area | Property is in a locality the lender treats as hard to sell, hard to verify, legally messy, or socially sensitive; the issue is collateral risk, not borrower credit. Public reporting shows lenders have used “negative” / “black” / “grey” area lists, but exact localities vary by lender and are not publicly published in a usable master list. | Banks/HFCs with local risk filters; exact lender names and pincodes are usually not public. | Conditional/Decline(varies) | Partial | Ask the exact lender for a locality check before token booking; get title search, municipal approvals, and RERA/plan-sanction verification. | Livemint, Lonatips |



| Cash-salary applicant | The bank statement is ground truth — it's the one document that can't be faked and overrides everything the applicant claims. A cash-salary applicant doesn't have a weaker version of ground truth; they have none. There's no salary credit to verify against, no trail. So it's not that their income is "harder to verify" — it's that the lender's entire verification model has nothing to bite on. | Lender-specific; some will consider with stronger alternate proofs, some will be cautious. | Decline(Mainstream)/Conditional(NBFC) | Yes | Convert to banked income where possible, show longer bank-credit trail, ITRs, employer letters, or alternate income proofs. | Indianbank, Bajajhousingfinance |



| Restricted profession | Certain jobs are treated as higher risk because of income volatility, reputational risk, legal exposure, or lender policy (for example: politicians, lawyers, cash-based transport, liquor-related work, DSA/verification/collection roles, freelancers/media in some policies). Public sources show examples, but the exact “not allowed” list is highly lender-specific and inconsistent. Restricted-profession list is illustrative.| Mostly lender-policy specific; some bank/HFC internal credit-policy docs and DSA sheets. | Decline/Conditional(varies) | Partial | Shift from cash-based / informal proof to documented income, add co-applicant, lower LTV, or move to a lender that accepts the profile. | scribd, indianhomeloan.co |



| Profile red flags (thin file / enquiry burst / job-hopping) | Thin credit history makes risk harder to price; multiple hard enquiries signal credit hunger; frequent job changes can weaken income-stability assessment. Public sources consistently mention employment continuity and the harm from multiple enquiries, but thresholds vary by lender. | Broadly all lenders, but the exact score impact and cutoffs differ. | Rate-Load/Conditional | Yes | Slow new applications, reduce enquiry bursts, build credit depth, keep stable job history, and document promotions / continuity | shriramfinance, biddaro |



GAP: No public source names which exact pincodes any lender blacklists in a reliable, current, lender-by-lender way. What exists publicly is scattered reporting and generic “negative area” explainers; the real lists are typically internal and local-branch / DSA knowledge.



GAP: No public source gives a universal “restricted professions” master list for all lenders. The occupation filters vary sharply by bank/HFC, geography, and risk team.



GAP: Public sources rarely quantify how much each profile feature hurts approval odds. Whether a cash-salary case, job-hopper, or thin-file borrower is declined depends on lender policy, documentation quality, FOIR, property risk, and the officer’s discretion.



SOURCE NOTE: Negative-profile sourcing is low-tier by nature — the authoritative lists are internal/DSA-only. Public sources confirm categories exist but not specifics. Treat this entire section as concept-verified, specifics-unverified, DSA-required.



\## === MASTER GAP LIST - what only a DSA can tell me === (The precise, scoped questions to ask a working  DSA. This IS the week's deliverable.)



GAP Questions for DSA

Which exact pincodes/areas are blacklisted by this lender today?

Public sources confirm “negative area” lists exist, but not the live, lender-by-lender locality list. Ask for the current internal locality screen and whether it is branch-specific or centralized.



Which professions does this lender classify as restricted, caution, or declined?

Public pages mention that employer/profession filters exist, but they do not publish a universal occupation blacklist. Ask for the internal profession matrix and whether any role is auto-decline versus manual review.



What is the lender’s exact employer-category logic for Cat A / B / C?

The concept is public, but the company list is proprietary and can differ by lender. Ask whether the employer is on the approved list, what category it falls into, and whether the same employer changes status by branch or region.



What is the exact rate-load or FOIR penalty for Cat C or lower-ranked employers?

Public sources usually say “rate-load” or “more checks,” but not the actual bps or FOIR haircut. Ask for the precise impact on sanction amount, pricing, or tenure.



Does this lender accept cash-salary cases, and if yes, what alternate proofs are mandatory?

Public sources show income proof matters, but they do not reveal each lender’s cash-income tolerance. Ask whether cash income can be underwritten, and whether bank credits, ITRs, employer letters, or field verification can substitute for salary slips.



How long must job stability be for this lender to ignore recent switching or probation?

Public sources support the idea that tenure matters, but not the exact minimum months for each lender. Ask about probation, minimum current-employer tenure, and whether a recent job switch is decline, delay, or manual override.



How many hard enquiries are too many for this lender, and over what time window?

Public sources warn against enquiry bursts, but not the lender’s cutoff. Ask for the enquiry threshold, lookback period, and whether recent bureau pulls can be offset by strong income or collateral.



What documentation can rescue a property that is borderline on OC, APF, title, or valuation?

Public pages explain the concepts, but not which combinations of papers are enough for a lender override. Ask for the exact checklist: completion certificate, approved plan, tax receipts, legal opinion, technical valuation, APF addition path, or valuation appeal process.



For each lender: which co-applicant relationships are allowed (spouse, parents, siblings?), what percentage of the co-applicant's income is clubbed (100% or a haircut?), and are the co-applicant's own existing EMIs also added to the FOIR calculation?



What's HDFC's actual minimum CIBIL — hard floor vs. rate-load threshold?

