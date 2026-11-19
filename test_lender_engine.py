import json
from lender_engine import lender_sanction

with open("lenders/hdfc.json") as f:
    hdfc = json.load(f)
with open("lenders/icici.json") as f:
    icici = json.load(f)

weak_cibil_borrower = {
    "net_income": 150000,
    "existing_emis": 18000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 690,
}

hdfc_result = lender_sanction(weak_cibil_borrower, hdfc)
assert hdfc_result["binding"] != "DECLINE", "HDFC should NOT hard-decline on a partial-confidence CIBIL floor"
assert hdfc_result["sanction"] == 6000000, "HDFC sanction changed: got " + str(hdfc_result["sanction"])
assert any("soft gradient" in f for f in hdfc_result["flags"]), "HDFC should flag the soft-gradient CIBIL caveat"

icici_result = lender_sanction(weak_cibil_borrower, icici)
assert icici_result["binding"] == "DECLINE", "ICICI should hard-decline on a verified CIBIL floor breach"
assert icici_result["sanction"] == 0, "ICICI sanction should be 0 on decline, got " + str(icici_result["sanction"])
assert any("DECLINED" in f for f in icici_result["flags"]), "ICICI should carry a DECLINED flag"

print("Case 1 (weak CIBIL 690) - PASSED: HDFC sanctions with caveat, ICICI hard-declines")

strong_cibil_borrower = dict(weak_cibil_borrower)
strong_cibil_borrower["cibil"] = 750

hdfc_result2 = lender_sanction(strong_cibil_borrower, hdfc)
assert hdfc_result2["binding"] != "DECLINE", "HDFC should never decline a 750 CIBIL borrower"
assert hdfc_result2["sanction"] == 6000000, "HDFC sanction changed at 750 CIBIL: " + str(hdfc_result2["sanction"])
assert not any("soft gradient" in f for f in hdfc_result2["flags"]), "HDFC should NOT show CIBIL caveat when borrower clears the floor"

icici_result2 = lender_sanction(strong_cibil_borrower, icici)
assert icici_result2["binding"] != "DECLINE", "ICICI should NOT decline a 750 CIBIL borrower"
assert icici_result2["sanction"] == 6000000, "ICICI sanction changed at 750 CIBIL: " + str(icici_result2["sanction"])
assert any("RATE STALE" in f for f in icici_result2["flags"]), "ICICI should still flag its stale rate source regardless of CIBIL"

print("Case 2 (strong CIBIL 750) - PASSED: both lenders sanction, ICICI still flags stale rate")

for result, label in [(hdfc_result2, "HDFC"), (icici_result2, "ICICI")]:
    assert result["sanction"] <= strong_cibil_borrower["property_value"], \
        label + " sanctioned MORE than the property value - likely a unit/scale bug: " + str(result["sanction"])

print("Sanity tripwire - PASSED: no sanction exceeds property value")
print()
print("ALL TESTS PASSED") 
# --- Case 3: Axis has no hard CIBIL floor at all (verified_absence) ---
with open("lenders/axis.json") as f:
    axis = json.load(f)

axis_result_weak = lender_sanction(weak_cibil_borrower, axis)
assert axis_result_weak["binding"] != "DECLINE", "Axis has no hard floor - should never decline on CIBIL"
assert axis_result_weak["sanction"] == 6000000, "Axis sanction unexpected: " + str(axis_result_weak["sanction"])
assert not any("CIBIL" in f for f in axis_result_weak["flags"]), "Axis should not raise a CIBIL caveat - it has no stated floor to be below"

axis_result_strong = lender_sanction(strong_cibil_borrower, axis)
assert axis_result_strong["binding"] != "DECLINE"
assert axis_result_strong["sanction"] == 6000000

print("Case 3 (Axis, no CIBIL floor) - PASSED: never declines, never raises a CIBIL caveat")
print()
print("ALL TESTS PASSED (HDFC, ICICI, Axis)")
# --- Case 4: Bajaj HFC schema - rate keyed by employment_type, not "effective_min" ---
with open("lenders/bajaj.json") as f:
    bajaj = json.load(f)

bajaj_result = lender_sanction(weak_cibil_borrower, bajaj)
assert round(bajaj_result["rate_pct"], 2) == 7.25, "Bajaj salaried rate should read 7.25 from salaried_min, got " + str(bajaj_result["rate_pct"])
assert bajaj_result["binding"] != "DECLINE", "Bajaj min_cibil is partial confidence - should not hard-decline at 690"
assert any("soft gradient" in f for f in bajaj_result["flags"]), "Bajaj should flag the soft CIBIL caveat at 690"

print("Case 4 (Bajaj, salaried_min rate key) - PASSED: reads 7.25% correctly, soft CIBIL caveat not decline")
print()
print("ALL TESTS PASSED (HDFC, ICICI, Axis, Bajaj)")
# --- Case 5: LIC HFL - salaried_min rate key (Bajaj-style) + verified_absence CIBIL (Axis-style) ---
with open("lenders/lichfl.json") as f:
    licfhl = json.load(f)

licfhl_result = lender_sanction(weak_cibil_borrower, licfhl)
assert round(licfhl_result["rate_pct"], 2) == 7.15, "LIC HFL salaried rate should read 7.15, got " + str(licfhl_result["rate_pct"])
assert licfhl_result["binding"] != "DECLINE", "LIC HFL has no CIBIL floor - should never decline on CIBIL"
assert not any("CIBIL" in f for f in licfhl_result["flags"]), "LIC HFL should not raise a CIBIL caveat - no stated floor"

print("Case 5 (LIC HFL, salaried_min + no CIBIL floor) - PASSED: reads 7.15% correctly, no CIBIL flag")
print()
print("ALL TESTS PASSED (HDFC, ICICI, Axis, Bajaj, LIC HFL)")