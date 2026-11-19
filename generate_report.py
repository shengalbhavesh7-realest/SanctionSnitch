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
