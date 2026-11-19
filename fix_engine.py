from emi import foir_ceiling, max_principal
from lender_engine import get_ltv_ceiling, get_rate_pct

TICKET_REDUCTION_THRESHOLD_PCT = 0.10

def compute_shortfall(borrower, sanction_result):
    available_funds = borrower.get("available_own_funds", 0)
    loan_required = borrower["property_value"] - available_funds
    shortfall = loan_required - sanction_result["sanction"]
    return loan_required, shortfall

def fix_extend_tenure(borrower, lender_json, sanction_result, loan_required):
    if sanction_result["binding"] != "FOIR":
        return None
    current_tenure = sanction_result["tenure_years"]
    lender_max = lender_json["max_tenure_years"]["value"]
    if current_tenure >= lender_max:
        return None

    flags = []
    rate_pct = get_rate_pct(lender_json["rate_band"], borrower["employment_type"], flags)
    foir_cap = 0.50
    available_emi = borrower["net_income"] * foir_cap - borrower["existing_emis"]
    if available_emi <= 0:
        return None

    extended_sanction = round(max_principal(available_emi, rate_pct, lender_max))
    impact = extended_sanction - sanction_result["sanction"]
    if impact <= 0:
        return None

    return {
        "fix": "Extend tenure",
        "detail": "Age caps this lender's tenure at " + str(current_tenure) + " yrs (lender max is " + str(lender_max) + " yrs). Reaching the full " + str(lender_max) + "-yr tenure - typically via a younger co-applicant - raises the FOIR-based ceiling.",
        "impact_rs": impact,
        "closes_shortfall_pct": None,
    }

def fix_reduce_ticket(borrower, lender_json, sanction_result, loan_required):
    if sanction_result["binding"] != "LTV":
        return None

    property_value = borrower["property_value"]
    ltv_slabs = lender_json["ltv_slabs"]
    keys = set(k for k in ltv_slabs.keys() if not k.startswith("_"))

    if keys != {"upto_30L", "30L_to_75L", "above_75L"}:
        return None

    if property_value <= 7500000:
        return None

    boundary = 7500000
    distance_pct = (property_value - boundary) / boundary
    if distance_pct > TICKET_REDUCTION_THRESHOLD_PCT:
        return None

    new_sanction = round(boundary * ltv_slabs["30L_to_75L"])
    new_loan_required = boundary - borrower.get("available_own_funds", 0)
    new_shortfall = new_loan_required - new_sanction
    old_shortfall = loan_required - sanction_result["sanction"]
    impact = old_shortfall - new_shortfall

    if impact <= 0:
        return None

    return {
        "fix": "Negotiate price down to Rs " + format(boundary, ","),
        "detail": "Property is " + str(round(distance_pct * 100, 1)) + "% above the Rs 75L LTV slab boundary. Crossing below it moves the lender from 75% to 80% LTV.",
        "impact_rs": impact,
        "closes_shortfall_pct": None,
    }

def fix_close_liability(borrower, lender_json, sanction_result, loan_required):
    if sanction_result["binding"] != "FOIR":
        return None
    if borrower["existing_emis"] <= 0:
        return None

    flags = []
    rate_pct = get_rate_pct(lender_json["rate_band"], borrower["employment_type"], flags)
    tenure = sanction_result["tenure_years"]
    foir_cap = 0.50

    sanction_no_liability = round(foir_ceiling(borrower["net_income"], 0, foir_cap, rate_pct, tenure))
    impact = sanction_no_liability - sanction_result["sanction"]
    if impact <= 0:
        return None

    return {
        "fix": "Close existing liability (Rs " + format(borrower["existing_emis"], ",") + "/mo EMI)",
        "detail": "Fully closing current EMI obligations before application would free this much FOIR headroom at this lender.",
        "impact_rs": impact,
        "closes_shortfall_pct": None,
    }

def get_fixes(borrower, lender_json, sanction_result):
    if sanction_result["binding"] == "DECLINE":
        return []

    loan_required, shortfall = compute_shortfall(borrower, sanction_result)
    if shortfall <= 0:
        return []

    candidates = [
        fix_extend_tenure(borrower, lender_json, sanction_result, loan_required),
        fix_reduce_ticket(borrower, lender_json, sanction_result, loan_required),
        fix_close_liability(borrower, lender_json, sanction_result, loan_required),
    ]
    fixes = [f for f in candidates if f is not None]

    for f in fixes:
        f["closes_shortfall_pct"] = round(min(f["impact_rs"] / shortfall, 1.0) * 100, 1)

    fixes.sort(key=lambda f: f["impact_rs"], reverse=True)
    return fixes