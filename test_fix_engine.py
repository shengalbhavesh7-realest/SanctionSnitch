import json
from lender_engine import lender_sanction
from fix_engine import get_fixes, compute_shortfall

with open("lenders/hdfc.json") as f:
    hdfc = json.load(f)

borrower = {
    "net_income": 80000,
    "existing_emis": 15000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 6000000,
    "cibil": 750,
}

result = lender_sanction(borrower, hdfc)
print("HDFC sanction:", result["sanction"], "| binding:", result["binding"])

loan_required, shortfall = compute_shortfall(borrower, result)
print("Loan required:", loan_required, "| Shortfall:", shortfall)

fixes = get_fixes(borrower, hdfc, result)
assert len(fixes) > 0, "Expected at least one fix for a FOIR-bound borrower with a real shortfall"
for f in fixes:
    print("-", f["fix"], "| impact Rs", format(f["impact_rs"], ","), "| closes", f["closes_shortfall_pct"], "% of shortfall")
    print(" ", f["detail"])

print()
print("Test 2: borrower with NO shortfall - expect zero fixes")
strong_borrower = dict(borrower)
strong_borrower["net_income"] = 300000
strong_borrower["existing_emis"] = 0
strong_borrower["property_value"] = 3000000
strong_result = lender_sanction(strong_borrower, hdfc)
strong_fixes = get_fixes(strong_borrower, hdfc, strong_result)
print("Sanction:", strong_result["sanction"], "| property:", strong_borrower["property_value"], "| fixes:", len(strong_fixes))
assert len(strong_fixes) == 0, "Should have zero fixes when sanction already covers the requirement"

print()
print("Test 3: LTV-bound borrower just above the 75L boundary - ticket-size fix should fire")
boundary_borrower = {
    "net_income": 200000,
    "existing_emis": 10000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7800000,
    "cibil": 750,
}
boundary_result = lender_sanction(boundary_borrower, hdfc)
print("Sanction:", boundary_result["sanction"], "| binding:", boundary_result["binding"])
boundary_fixes = get_fixes(boundary_borrower, hdfc, boundary_result)
ticket_fix = [f for f in boundary_fixes if "Negotiate" in f["fix"]]
assert len(ticket_fix) == 1, "Expected the ticket-size fix to fire within 10% of the boundary"
print("-", ticket_fix[0]["fix"], "| impact Rs", format(ticket_fix[0]["impact_rs"], ","))

print()
print("Test 4: property FAR above boundary (30%) - ticket-size fix should NOT fire")
far_borrower = dict(boundary_borrower)
far_borrower["property_value"] = 9750000
far_result = lender_sanction(far_borrower, hdfc)
far_fixes = get_fixes(far_borrower, hdfc, far_result)
far_ticket_fix = [f for f in far_fixes if "Negotiate" in f["fix"]]
assert len(far_ticket_fix) == 0, "Ticket-size fix should NOT fire when 30% above boundary"
print("Correctly suppressed - property too far from slab boundary")

print()
print("ALL FIX ENGINE TESTS PASSED")