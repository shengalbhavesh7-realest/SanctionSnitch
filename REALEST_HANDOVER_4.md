# REALEST HANDOVER 4

Continuation of REALEST_HANDOVER_3.md. This doc captures everything needed to pick up work in a fresh chat with zero context loss.

Project root: `C:\Users\HP\realest`
Brand name (correct, use everywhere): **Realest - Finance, AI and Investments**
(Earlier "Capital and Investments" naming is deprecated - if you see it anywhere, it's stale and should be corrected.)

---

## 1. WHAT THIS SESSION ACCOMPLISHED

Starting point: the lender-comparison engine (`run_all_lenders.py`, `lender_engine.py`, `fix_engine.py`, `emi.py`, `processing_fee.py`, `borrower_input.py`) was already built and tested from prior sessions. This session's job was Phase 8: build a branded, client-facing PDF report generator on top of that engine.

Delivered this session:
1. **`generate_report.py`** - new file, builds a one-page branded PDF report from the engine's output. Verified working end-to-end on the user's machine multiple times.
2. **A real bug fix in `lender_engine.py`** - SBI's `min_cibil.aggregator_claim` data existed in `sbi.json` but was never being read; the flag logic only checked `.value` (which is `null` for SBI) and fell back to a generic "UNKNOWN" message. Fixed to surface the actual unofficial CIBIL range when `aggregator_claim` data exists. Full regression-tested, zero breakage.
3. Multiple rounds of real bugs found and fixed in `generate_report.py` (see Section 4 - do not re-introduce these).

---

## 2. FILE STATUS: WHAT'S VERIFIED-CURRENT

| File | Status | Notes |
|---|---|---|
| `run_all_lenders.py` | Verified-current (unchanged this session) | Confirmed via `type` early this session, matches prior handover exactly |
| `lender_engine.py` | **Changed and verified-current** | SBI CIBIL fix applied, full test suite re-run and passing (see Section 3) |
| `generate_report.py` | **New, verified-current** | Full content in Section 5. Tested on user's real machine multiple times plus sandbox-rendered/visually-checked by the assistant |
| `fix_engine.py`, `emi.py`, `processing_fee.py`, `borrower_input.py` | Not touched this session | Assumed still verified-current from prior handover - not re-checked this session, worth a `type` confirm if anything seems off |
| `sbi.json`, `hdfc.json`, `icici.json`, `axis.json`, `bajaj.json`, `lichfl.json` | `sbi.json` inspected closely; others NOT inspected this session | See Section 7 (open risk) |

---

## 3. THE lender_engine.py FIX (DETAIL)

**Root cause found by the user**, not by the assistant - the user personally read `sbi.json` and noticed `aggregator_claim` data sitting unused next to a `null` `value` field, and asked why the flag said "unknown" instead of giving a range.

**Location:** `lender_sanction()` function, the `min_cibil` handling block (was lines 65-66 in the pre-fix version).

**Before:**
```python
if min_cibil is None and cibil_confidence == "unknown":
    flags.append("CIBIL requirement UNKNOWN for this lender - no official floor published, unverified third-party claims exist. Do not assume approval on CIBIL alone.")
```

**After:**
```python
if min_cibil is None and cibil_confidence == "unknown":
    aggregator_claim = cibil_data.get("aggregator_claim")
    if aggregator_claim:
        claim_parts = [k.replace("_", "-") + ": " + v for k, v in aggregator_claim.items()]
        claim_summary = "; ".join(claim_parts)
        flags.append("CIBIL requirement UNOFFICIAL for this lender - no official floor published. Unverified third-party range: " + claim_summary + ". Do not assume approval on CIBIL alone.")
    else:
        flags.append("CIBIL requirement UNKNOWN for this lender - no official floor published, unverified third-party claims exist. Do not assume approval on CIBIL alone.")
```

**Design intent:** generic across all lenders, not an SBI-only hack. Any lender whose JSON has an `aggregator_claim` dict under `min_cibil` will now get the range-based flag; lenders without it (Axis, LIC HFL, confirmed via test suite) silently fall through to the old generic message, unchanged.

**Real-world corroboration:** the assistant web-searched SBI's actual CIBIL practice mid-session and found genuine third-party disagreement clustering around 650-750, which matches `sbi.json`'s own `aggregator_claim` values (650/699 tiers, 700+ "good") - so the range being surfaced isn't fabricated, it reflects real conflicting public claims.

**Testing performed:** user ran all three test files directly (`python test_lender_engine.py`, `python test_sbi_and_regression.py`, `python test_edge_cases.py` - **not pytest**, these are plain scripts with print-based pass/fail, no pytest installed on the machine). All passed:
- `test_lender_engine.py`: 5 cases (HDFC, ICICI, Axis, Bajaj, LIC HFL) - all passed
- `test_sbi_and_regression.py`: SBI-specific + regression check confirming HDFC/ICICI/Axis/Bajaj/LIC HFL unchanged - all passed
- `test_edge_cases.py`: 16 edge cases (age/retirement, self-employed, exact slab boundaries, exact CIBIL floor, FOIR exhaustion, high income, young borrower, low property value, three-way rate tiers, multi-flag accumulation, zero shortfall, declined-lender zero-fixes, co-applicant field ignored, full pipeline integration, past-retirement decline) - all 16 passed

No test asserted the exact old "CIBIL requirement UNKNOWN..." string, so nothing broke from the wording change.

---

## 4. generate_report.py: BUGS FOUND AND FIXED THIS SESSION (DO NOT RE-INTRODUCE)

This file went through several real bugs before reaching its current state. Documenting each so future edits don't reintroduce them:

1. **Mojibake / encoding artifacts.** First draft used real em-dash (—) and bullet (•) characters. When the user ran `type generate_report.py` in Command Prompt, these rendered as `ΓÇö` and `ΓÇó` garbage because cmd.exe's console codepage isn't UTF-8 by default. The script would likely have still run fine (Python 3 reads `.py` source as UTF-8 regardless), but this was fixed anyway by stripping the file to **pure ASCII** - all em-dashes and bullets replaced with plain hyphens (`-`). **Rule going forward: keep this file (and any file handed to this user via Notepad/cmd) ASCII-only to avoid this entirely.**

2. **File-lock crash.** Running `generate_report.py` while the previously-generated PDF is still open in a viewer (e.g. Edge) throws `PermissionError: [Errno 13] Permission denied` on `doc.build(story)` / `canvas.save()`. This is a Windows file-lock issue, not a code bug. **Partially mitigated** by the timestamp-filename fix in item 4 below (different filename each run = no more collision with a currently-open file from a *previous* run), but if the user runs twice within the same second, or reopens and holds a specific timestamped file open while trying to regenerate to that exact name, it could theoretically still occur. Not fully bulletproofed with a retry/fallback; low priority given the timestamp fix already resolves the common case.

3. **Recommendation box table had a colWidths/cell-count mismatch.** The `reco_table` had a row with **two** Paragraph cells (lender name + sanction details) but was defined with only **one** `colWidths` entry (`[170*mm]`). This caused the lender name column to collapse to near-zero width, making the bold lender name (e.g. "LIC HOUSING FINANCE") effectively invisible in the rendered PDF - the box looked like it had an empty left side. **This shipped to the user twice before being caught** (user had to point it out after being told the report was "broker-ready"). Fixed by giving explicit two-column widths: `colWidths=[60 * mm, 110 * mm]`, plus `VALIGN: MIDDLE` so the two cells align vertically. **Lesson explicitly logged per user's own request: always visually render and check any multi-cell table row before considering the file done, not just read the code and assume correctness.**

4. **Filename collision.** Original code always wrote to a fixed `realest_report.pdf`, meaning every regeneration silently overwrote the previous client's report with no warning - a real data-loss risk for actual multi-client use. Fixed: `run_live_report()` now generates `realest_report_YYYYMMDD_HHMMSS.pdf` via `datetime.datetime.now().strftime(...)`. Verified end-to-end in sandbox (confirmed file `realest_report_20260817_074317.pdf` actually written with correct unique name). **Note:** borrower name/initials were considered for the filename instead of a timestamp, but **no name field exists anywhere in the borrower data structure** (confirmed by inspecting every borrower dict shown throughout this session: `net_income`, `existing_emis`, `age`, `employment_type`, `property_value`, `available_own_funds`, `cibil` - no name). Timestamp was chosen specifically because it needs no new input collection. If per-client filenames become a real need, `collect_borrower()` in `borrower_input.py` would need a name/reference field added first - not done this session.

5. **Spacing was too tight throughout** (multiple rounds of user feedback: "does not look good," "look at the heading? no spacing," "look at the top?"). Fixed iteratively:
   - `style_section` (all section headers): `spaceBefore` 8→13, `spaceAfter` 3→8 (went through several intermediate values before landing here - see Section 5 for final numbers)
   - Header band internal padding increased and balanced (title-to-tagline gap, tagline-to-bottom-edge gap)
   - Document `topMargin` changed from 10mm to 13mm to visually match the 15mm left/right margins (was previously noticeably thinner than the sides)
   - Table cell padding increased throughout (borrower snapshot, comparison table, fix table all went from ~3pt to ~5-6pt top/bottom padding)
   - **One regression caught and fixed within this same pass:** an early spacing-increase attempt pushed the report to 2 pages (footer text overflowed by 3 words). Caught by the assistant rendering and page-counting before sending to the user, not after - corrected by trimming `style_section` and `style_flag` spacing slightly and reducing `topMargin` from 15mm back to 13mm, until it returned to exactly one page while keeping real breathing room. **This is the current final state - it fits one page with visible margin to spare at the bottom (see the "all-decline" test render, which is the shortest content case, and the "with-fixes" test render, which is close to the longest realistic case - both comfortably one page).**

**Explicit process change adopted mid-session, at the user's prompting:** the assistant now renders `generate_report.py` output to an actual PDF, converts it to a PNG via `pdftoppm`, and visually inspects it (via the `view` tool) **before** handing any layout change back to the user. This should continue for any future layout edit to this file. Do not just read the code and assert correctness - the colWidths bug (item 3) is the direct counterexample of why that's not sufficient.

---

## 5. CURRENT FULL CONTENT OF generate_report.py

This is the exact, complete, verified-current version as of end of this session. If starting a new chat, this can be pasted directly - no need to re-derive.

```python
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from run_all_lenders import load_lenders, run_all_lenders, LENDER_FILES
from borrower_input import collect_borrower

BRAND_NAME = "REALEST - FINANCE, AI AND INVESTMENTS"
BRAND_TAGLINE = "Loan Eligibility & Lender Comparison Report"
BRAND_DARK = colors.HexColor("#122540")
BRAND_ACCENT = colors.HexColor("#c98a2c")
LIGHT_GREY = colors.HexColor("#f2f2f2")
MID_GREY = colors.HexColor("#666666")

styles = getSampleStyleSheet()

style_brand = ParagraphStyle(
    "Brand", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=15, textColor=colors.white, alignment=TA_LEFT, spaceAfter=0,
)
style_tagline = ParagraphStyle(
    "Tagline", parent=styles["Normal"], fontName="Helvetica",
    fontSize=9, textColor=colors.white, alignment=TA_LEFT,
)
style_section = ParagraphStyle(
    "Section", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=10, textColor=BRAND_DARK, spaceBefore=13, spaceAfter=8,
)
style_body = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5,
    leading=13,
)
style_small = ParagraphStyle(
    "Small", parent=styles["Normal"], fontName="Helvetica", fontSize=7,
    textColor=MID_GREY, leading=10,
)
style_reco_title = ParagraphStyle(
    "RecoTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=11, textColor=BRAND_DARK,
)
style_flag = ParagraphStyle(
    "Flag", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5,
    textColor=colors.HexColor("#8a2c1f"), leading=11, spaceAfter=1,
)


def rs(n):
    if n is None:
        return "-"
    return "Rs " + format(int(round(n)), ",")


def build_header(story):
    header_table = Table(
        [[Paragraph(BRAND_NAME, style_brand)],
         [Paragraph(BRAND_TAGLINE, style_tagline)]],
        colWidths=[170 * mm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_DARK),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (0, 0), 12),
        ("BOTTOMPADDING", (0, 0), (0, 0), 6),
        ("TOPPADDING", (0, 1), (0, 1), 0),
        ("BOTTOMPADDING", (0, 1), (0, 1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))


def build_borrower_snapshot(story, borrower):
    story.append(Paragraph("BORROWER SNAPSHOT", style_section))
    today = datetime.date.today().strftime("%d %b %Y")
    rows = [
        ["Net monthly income", rs(borrower["net_income"]), "Age", str(borrower["age"])],
        ["Existing EMI outflow", rs(borrower["existing_emis"]), "Employment", borrower["employment_type"].replace("_", " ").title()],
        ["Property value", rs(borrower["property_value"]), "CIBIL", str(borrower.get("cibil", "Not provided"))],
        ["Own funds available", rs(borrower.get("available_own_funds", 0)), "Report date", today],
    ]
    t = Table(rows, colWidths=[45 * mm, 40 * mm, 35 * mm, 50 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), MID_GREY),
        ("TEXTCOLOR", (2, 0), (2, -1), MID_GREY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))


def build_recommendation(story, top):
    story.append(Paragraph("RECOMMENDED LENDER", style_section))
    if top is None or top["binding"] == "DECLINE":
        story.append(Paragraph(
            "No lender approved this application as entered. See comparison table below for decline reasons.",
            style_body))
        return

    reco_rows = [[
        Paragraph(top["lender"].upper(), style_reco_title),
        Paragraph(
            "Sanction: <b>" + rs(top["sanction"]) + "</b>  |  Rate: <b>" +
            str(round(top["rate_pct"], 2)) + "%</b>  |  Tenure: <b>" +
            str(top["tenure_years"]) + " yrs</b>  |  Binding: " + top["binding"],
            style_body),
    ]]
    reco_table = Table(reco_rows, colWidths=[60 * mm, 110 * mm])
    reco_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("BOX", (0, 0), (-1, -1), 0.75, BRAND_ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(reco_table)

    cash = top["cash"]
    if top["processing_fee_amount"] is None:
        cash_line = ("Cash needed to close (processing fee not available - verify with lender): " +
                     rs(cash["total_cash"]))
    else:
        cash_line = ("Cash needed to close (incl. processing fee " + rs(cash["processing"]) +
                     "): " + rs(cash["total_cash"]))
    story.append(Spacer(1, 7))
    story.append(Paragraph(cash_line, style_body))

    if top["shortfall"] > 0:
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "SHORTFALL: " + rs(top["shortfall"]) + " vs " + rs(top["loan_required"]) + " required",
            ParagraphStyle("ShortfallHead", parent=style_body, fontName="Helvetica-Bold",
                           textColor=colors.HexColor("#8a2c1f"), spaceAfter=3)))
        if top["fixes"]:
            fix_rows = [["Fix", "Rupee impact", "% of shortfall closed"]]
            for f in top["fixes"]:
                fix_rows.append([f["fix"], rs(f["impact_rs"]), str(f["closes_shortfall_pct"]) + "%"])
            fix_table = Table(fix_rows, colWidths=[95 * mm, 40 * mm, 35 * mm])
            fix_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(Spacer(1, 6))
            story.append(fix_table)
        else:
            story.append(Paragraph(
                "No computable fix - may need co-applicant clubbing (DSA-gated, impact not quantified).",
                style_small))
    else:
        story.append(Spacer(1, 6))
        story.append(Paragraph("No shortfall - sanction covers the required loan amount.", style_body))

    story.append(Spacer(1, 8))


def build_comparison_table(story, ranked_results):
    story.append(Paragraph("FULL LENDER COMPARISON", style_section))
    header = ["Lender", "Status", "Sanction", "Rate", "Tenure", "Cash to close"]
    rows = [header]
    for r in ranked_results:
        if r["binding"] == "DECLINE":
            rows.append([r["lender"], "DECLINED", "-", "-", "-", "-"])
        else:
            cash_val = rs(r["cash"]["total_cash"]) if r.get("processing_fee_amount") is not None else rs(r["cash"]["total_cash"]) + "*"
            rows.append([
                r["lender"], r["binding"], rs(r["sanction"]),
                str(round(r["rate_pct"], 2)) + "%", str(r["tenure_years"]) + " yrs", cash_val,
            ])
    t = Table(rows, colWidths=[30 * mm, 25 * mm, 32 * mm, 20 * mm, 22 * mm, 41 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 4))
    story.append(Paragraph("* processing fee not available for this lender, excluded from cash figure - verify directly", style_small))
    story.append(Spacer(1, 6))


def build_flags(story, ranked_results):
    all_flags = []
    for r in ranked_results:
        for f in r.get("flags", []):
            all_flags.append(r["lender"] + ": " + f)
    if not all_flags:
        return
    story.append(Paragraph("RISK FLAGS & NOTES", style_section))
    for f in all_flags:
        story.append(Paragraph("- " + f, style_flag))
    story.append(Spacer(1, 10))


def build_footer(story):
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This is an informational lender-comparison analysis based on figures provided by the borrower/broker "
        "at the time of this report, and does not constitute a loan sanction, approval, or offer. Final terms "
        "are determined solely by the lender after their own underwriting and document verification. "
        "Prepared by Realest - Finance, AI and Investments.",
        style_small))


def generate_pdf_report(borrower, ranked_results, output_path="realest_report.pdf"):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=13 * mm, bottomMargin=10 * mm,
    )
    story = []
    build_header(story)
    build_borrower_snapshot(story, borrower)

    top = ranked_results[0] if ranked_results else None
    build_recommendation(story, top)
    build_comparison_table(story, ranked_results)
    build_flags(story, ranked_results)
    build_footer(story)

    doc.build(story)
    print("Report saved to:", output_path)


def run_live_report():
    lenders = load_lenders(LENDER_FILES)
    borrower = collect_borrower()
    print()
    ranked = run_all_lenders(borrower, lenders)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = "realest_report_" + timestamp + ".pdf"
    generate_pdf_report(borrower, ranked, output_path)


if __name__ == "__main__":
    run_live_report()
```

**File is pure ASCII.** No em-dashes, no smart quotes, no bullets. Keep it that way.

---

## 6. RENDERING PATHS VERIFIED (AND HOW)

Every code path the PDF generator can actually hit has now been checked, either on the user's real machine or via a sandbox mock-data harness (constructing fake `ranked_results` dicts matching the exact shape `run_all_lenders()` produces, importing `generate_report.py` with `run_all_lenders`/`borrower_input` stubbed out, calling `generate_pdf_report()` directly, then converting the output to PNG via `pdftoppm` and visually inspecting it):

| Scenario | Verified on | Result |
|---|---|---|
| Clean approval, no shortfall | User's real machine | One page, correct |
| Shortfall, no computable fix | User's real machine | One page, correct, red shortfall text renders |
| Shortfall, WITH computable fixes (populated fix table) | Sandbox mock | One page, correct - this path had never been seen with real data until this check |
| All lenders declined / no approval at all | Sandbox mock | One page, correct - "No lender approved..." message and DECLINED rows both render cleanly |
| SBI unofficial-CIBIL-range flag | User's real machine | Renders correctly post-fix |
| Bajaj processing-fee-range flag + asterisk footnote | User's real machine | Renders correctly |
| ICICI rate-stale flag | User's real machine | Renders correctly |

**Not yet tested:** self-employed/professional employment type through the actual PDF (only tested through `lender_engine.py`'s own test suite, not visually through the report). Borrower with no CIBIL provided at all (blank input) through the actual PDF. Multiple simultaneous DECLINE + approved lenders mixed in the same comparison table (only all-approved and all-declined have been visually checked, not a mixed table - though this is low risk since it's just more rows of the same table logic already verified in isolation).

---

## 7. OPEN RISKS / NOT YET DONE

In rough priority order:

1. **FOIR cap is ASSUMED 0.5 for every single lender in every report generated so far.** This is the single biggest accuracy risk in the entire tool. It means every sanction amount computed by FOIR (not LTV) binding could be wrong if a lender's real FOIR cap differs from 50%. Real caps are DSA-gated (not publicly available without a broker relationship) - this is a genuine chicken-and-egg problem tied to Phase 6. Worth sourcing real FOIR caps for at least the top 1-2 lenders by volume once any broker relationship exists.

2. **Only `sbi.json` has been closely read this session.** The `aggregator_claim`-unused-data pattern that caused the CIBIL bug was found by the user manually reading one file. The other five lender JSONs (`hdfc.json`, `icici.json`, `axis.json`, `bajaj.json`, `lichfl.json`) have NOT been checked for the same pattern - there could be other sourced-but-unused data sitting in them. A `findstr /n "aggregator_claim\|_note\|_confidence" *.json` style pass across all six files would be a reasonable next step, low effort.

3. **File-lock error is not fully solved**, just made less likely (see Section 4, item 2). If it recurs, the fix would be a try/except around `doc.build()` with a fallback filename (e.g. append `_2`, `_3`) - not implemented, low priority given current mitigation.

4. **No per-client filename/reference** - reports are named by timestamp only, not by borrower. Fine for now; would need a name field added to `collect_borrower()` in `borrower_input.py` if this becomes a real requirement.

5. **Visual branding is text-only** (no logo image) - by design, per earlier decision, until a real visual identity exists. Not a bug, just a known limitation to revisit later.

6. **Co-applicant income clubbing is explicitly NOT implemented** - confirmed still true, `fix_engine.py`/`lender_engine.py` correctly ignore any `co_applicant_income` field without crashing or silently half-applying it (Edge Case 14 in the test suite locks this in as intended behavior, not a bug). DSA-gated data required before this could be implemented.

---

## 8. USER'S WORKING STYLE / CONVENTIONS (IMPORTANT - READ BEFORE PROCEEDING)

- **Full clean replace, not partial edits, for pasting into Notepad.** The user has had partial-edit/Notepad corruption issues before. When a file needs changing, give the complete file content to paste in fresh (Ctrl+A, Delete, paste, save), not a diff to manually apply.
- **Verify every paste with `type filename` before running anything.** Standard step, always do this.
- **Keep all files ASCII-only.** See Section 4, item 1 - non-ASCII characters render as mojibake in `cmd.exe`'s `type` output even though Python itself would likely handle them fine. Avoid the issue entirely rather than relying on that "likely."
- **The user runs everything themselves via Command Prompt + Notepad on Windows.** No IDE, no direct code execution access for the assistant on the user's actual machine - the assistant can only give exact commands and exact file content, then read back what the user pastes as screenshots or pasted terminal output.
- **User downloads files via the file-card download button, not copy-paste, for brand-new files.** Copy-paste-via-Notepad is reserved for edits to existing files or if a browser download misbehaves (e.g. saves as `.txt`).
- **User personally reads source JSON/code files closely and catches real bugs this way** (found the `aggregator_claim` issue, caught the colWidths/empty-box bug, caught the spacing/margin issues). Take their visual/detail observations seriously and verify rather than dismiss - twice this session, "hey does this look right?" from the user led to catching a real defect the assistant had not caught by reading its own code.
- **Test files are plain Python scripts with print-based pass/fail, run directly** (`python test_lender_engine.py`), NOT pytest-based. No pytest installed on the user's machine. Do not suggest pytest commands without first confirming pytest is actually installed.
- **The assistant should render and visually verify its own PDF/layout output (via sandbox tools: reportlab install, `pdftoppm` to PNG, `view` tool to inspect) before handing anything back**, rather than asserting correctness from reading code alone. This was explicitly called out by the user as a standard to hold going forward, after the colWidths bug shipped twice.

---

## 9. IMMEDIATE NEXT STEPS (PENDING USER DECISION)

As of end of this session, the user has not yet decided between:
- (a) Spot-checking the other 5 lender JSONs for unused sourced data (Section 7, item 2) - low effort, possible quick win
- (b) Moving straight to Phase 6: finding the first real broker relationship (the actual hard deadline - originally described as a ~5-month SOP clock, exact remaining time not restated this session)
- (c) Drafting the actual broker outreach message/pitch, which the assistant offered to help with but has not yet started

The tool itself (engine + PDF report) is considered feature-complete and broker-ready as of this session, pending only the open risks in Section 7 (none of which block using it, all of which are known limitations to communicate honestly if asked, especially item 1, the FOIR assumption).
