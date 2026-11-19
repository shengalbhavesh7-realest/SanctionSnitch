SanctionSnitch: what it is and how it was built

What it is



SanctionSnitch is a home-loan pre-qualification engine for Indian real estate deals. You give it a buyer’s profile and it tells you which of six lenders would finance them and how much, what is limiting the loan, what the buyer needs in cash to close, and what would fix any shortfall. It’s the specific product under the Realest brand, and it exists because deals often die at financing after everyone has already invested time in them.



What it does



Inputs: net monthly income, existing EMIs, age, employment type (salaried, self-employed, or professional), property value, own funds available, and CIBIL score if known.



For each of six lenders (HDFC, ICICI, Axis, Bajaj Housing, LIC Housing Finance, SBI), it computes:



The maximum sanction. Three ceilings are calculated and the lowest wins: an income ceiling (FOIR), a property ceiling (LTV slab), and a tenure ceiling (the lender’s retirement-age cap).

The binding constraint. For example, ₹1.5L income on a ₹75L property is capped at ₹60L by LTV, while ₹90K income on the same property is capped at about ₹40.58L by income. The fix differs depending on which one binds.

Rate and tenure, read from each lender’s own data.

Cash to close: down payment, stamp duty, registration, and the lender’s processing fee.

Shortfall and ranked fixes when the sanction falls short of what the buyer needs: extend tenure, close an existing liability, or negotiate the price below an LTV slab boundary. Each fix shows its rupee impact and what share of the gap it closes.



It handles real policy differences. ICICI has a hard CIBIL floor, HDFC and Bajaj have soft ones, Axis and LIC HFL have none, and SBI’s is unpublished. SBI has two LTV slabs where the others have three. Bajaj prices professionals separately, and a 54-year-old salaried buyer gets only six years of tenure at HDFC. The output is a ranked list with declines at the bottom, and a one-page branded PDF report.



How it was built



1\. A hard principle first. The calculation layer is deterministic Python with no LLM in it. A confidently wrong sanction number would destroy a broker’s trust, so every number has to trace back to sourced lender data or real math.



2\. The lender matrix. Before any engine code, six lender JSON files were researched, each field tagged with \_source and \_confidence (verified, partial, stale, unknown, or verified absence). The tags drive behavior: a verified CIBIL floor causes a decline, a partial one only adds a caveat.



3\. The core math (emi.py). EMI, its inverse max\_principal() (which turns an allowed EMI back into a maximum loan), FOIR, tenure, and cash-needed functions. This was hand-typed first and restructured into a pure module with tests kept separate.



4\. The lender engine (lender\_engine.py). One shared function reads any lender’s JSON. It normalizes the two rate formats and recognizes each lender’s LTV slab shape, and it errors loudly on an unknown shape instead of guessing. It also applies the four-state CIBIL logic and declines anyone already at or past a lender’s retirement age.



5\. Supporting layers. fix\_engine.py does the shortfall math and ranked fixes. processing\_fee.py handles four different fee schemas, and where a fee is a genuine range (Bajaj) it returns no number and a flag. run\_all\_lenders.py ranks the results and borrower\_input.py handles validated live input.



6\. The AI edge (extract\_salary\_slip.py). The Claude API can read a pasted salary slip into structured fields, but a deterministic check then tests whether gross minus deductions matches net. If it doesn’t, confidence is forced to low whatever the model claimed, and nothing reaches the engine without a human confirming it.



7\. The report. generate\_report.py produces the one-page PDF with borrower snapshot, recommended lender, comparison table, and risk flags.



The method



Work was one step at a time. Each file was fully replaced, then checked with type to confirm the paste landed, then run. Code was verified in a sandbox before you pasted it. Six test files cover the math, the lenders, SBI’s slab logic, the fix engine, processing fees, and 16 edge cases including exact slab boundaries, CIBIL at the floor, and age 54 and age 62 cases. A rendered-output check was added after a PDF column bug shipped twice. The code was written with AI assistance and you directed it and verified it, which is how it’s honestly described.



Bugs that shaped it

HDFC was wrongly declined at CIBIL 690. The cause was treating every CIBIL floor as hard, whatever its confidence.

Processing fees silently fell back to a default for four of six lenders, showing Axis at ₹30K instead of ₹60K.

A default of zero own funds made every buyer show a false shortfall.

A “professional” employment type crashed Bajaj.

Past-retirement-age borrowers produced a negative sanction.

A missing lender file crashed the whole run.



Almost none of these crashed. They produced plausible-looking wrong numbers, and the tests exist to catch exactly that.



What the research changed



Four anonymous buyer-style conversations with brokers all showed the same pattern: brokers don’t evaluate eligibility, they hand off to a bank contact, and project-level APF approval constrains which banks are even available. That shaped the positioning and the service-first decision, and a stamp-duty concession for women buyers turned up along the way.



What it doesn’t do yet

FOIR is assumed at 50% for every lender. Real caps are internal bank data and aren’t public. The report flags it, but the per-case flagging fix (showing the warning only when FOIR actually binds) is designed and verified in isolation and not yet applied to the real engine file.

Co-applicant income clubbing is not implemented, for the same data reason.

There’s no APF filter, so it can recommend a lender that has no approval for a given project.

Stamp duty defaults to Maharashtra rates with no state or gender logic yet.

Only six lenders, with SBI the only public-sector bank.

run\_all\_lenders.py and generate\_report.py need a fresh type check before you rely on them in front of anyone.

