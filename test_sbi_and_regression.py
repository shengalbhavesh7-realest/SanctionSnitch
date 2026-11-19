import json
from lender_engine import lender_sanction, get_ltv_ceiling

with open("lenders/hdfc.json") as f:
    hdfc = json.load(f)
with open("lenders/icici.json") as f:
    icici = json.load(f)
with open("lenders/axis.json") as f:
    axis = json.load(f)
with open("lenders/bajaj.json") as f:
    bajaj = json.load(f)
with open("lenders/lichfl.json") as f:
    licfhl = json.load(f)
with open("lenders/sbi.json") as f:
    sbi = json.load(f)

borrower = {
    "net_income": 150000,
    "existing_emis": 18000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 750,
}

for lender_json, expected_sanction, label in [
    (hdfc, 6000000, "HDFC"),
    (icici, 6000000, "ICICI"),
    (axis, 6000000, "Axis"),
    (bajaj, 6000000, "Bajaj"),
    (licfhl, 6000000, "LIC HFL"),
]:
    r = lender_sanction(borrower, lender_json)
    assert r["sanction"] == expected_sanction, label + " REGRESSED after LTV rewrite: got " + str(r["sanction"])
    assert r["binding"] == "LTV", label + " binding changed: got " + r["binding"]

print("Regression check - PASSED: HDFC, ICICI, Axis, Bajaj, LIC HFL all unchanged at 6,000,000 LTV-bound")

sbi_result = lender_sanction(borrower, sbi)
expected_sbi_ltv = 7500000 * 0.80
print("SBI sanction:", sbi_result["sanction"], "| binding:", sbi_result["binding"], "| rate:", sbi_result["rate_pct"])
assert sbi_result["sanction"] == round(expected_sbi_ltv), "SBI 2-slab LTV wrong: expected " + str(expected_sbi_ltv) + " got " + str(sbi_result["sanction"])
assert sbi_result["binding"] == "LTV"

assert get_ltv_ceiling(2000000, sbi["ltv_slabs"]) == 2000000 * 0.90
assert get_ltv_ceiling(2000001, sbi["ltv_slabs"]) == 2000001 * 0.80
assert get_ltv_ceiling(20000000, sbi["ltv_slabs"]) == 20000000 * 0.80

print("SBI 2-slab LTV - PASSED: correctly reads 20L boundary and 80% ceiling (not HDFC's 75L/75%)")

try:
    get_ltv_ceiling(5000000, {"weird_key": 0.5})
    print("FAILED: unrecognized LTV shape should have raised KeyError")
except KeyError:
    print("Unrecognized-shape guard - PASSED: raises loudly instead of guessing")

print()
print("ALL TESTS PASSED (HDFC, ICICI, Axis, Bajaj, LIC HFL, SBI)")