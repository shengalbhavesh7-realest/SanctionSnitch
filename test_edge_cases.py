import json
from lender_engine import lender_sanction
from fix_engine import get_fixes, compute_shortfall

with open("lenders/hdfc.json") as f:
    hdfc = json.load(f)

# --- Edge Case 1: age 54, near retirement, tenure squeeze ---
borrower_54 = {
    "net_income": 150000,
    "existing_emis": 0,
    "age": 54,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 750,
}

result = lender_sanction(borrower_54, hdfc)
print("Age 54 borrower at HDFC:")
print("  Sanction:", result["sanction"], "| Binding:", result["binding"], "| Tenure:", result["tenure_years"], "yrs")

assert result["tenure_years"] == 6, "Expected tenure capped at 6 yrs (60 - 54), got " + str(result["tenure_years"])

borrower_34 = dict(borrower_54)
borrower_34["age"] = 34
result_34 = lender_sanction(borrower_34, hdfc)
print("Age 34 borrower at HDFC (same income/property):")
print("  Sanction:", result_34["sanction"], "| Binding:", result_34["binding"], "| Tenure:", result_34["tenure_years"], "yrs")

assert result["sanction"] < result_34["sanction"], "54-year-old should have a LOWER sanction than 34-year-old due to shorter tenure"

print()
print("Edge Case 1 (near-retirement tenure squeeze) - PASSED")
print("  54yo sanction:", result["sanction"], "vs 34yo sanction:", result_34["sanction"],
      "-- age-driven gap of Rs", format(result_34["sanction"] - result["sanction"], ","))

# --- Edge Case 2: self_employed employment type ---
borrower_se = dict(borrower_54)
borrower_se["employment_type"] = "self_employed"

result_se = lender_sanction(borrower_se, hdfc)
print("Age 54, self-employed, at HDFC:")
print("  Sanction:", result_se["sanction"], "| Binding:", result_se["binding"], "| Tenure:", result_se["tenure_years"], "yrs")

assert result_se["tenure_years"] == 11, "Expected 11 yrs tenure (65-54) for self-employed, got " + str(result_se["tenure_years"])
assert result_se["sanction"] > result["sanction"], "Self-employed at same age should get MORE tenure and thus a higher sanction than salaried"

print()
print("Edge Case 2 (self-employed employment type) - PASSED")
print("  Self-employed (11yr tenure) sanction:", result_se["sanction"], "vs salaried (6yr tenure) sanction:", result["sanction"])

# --- Edge Case 3: property exactly at the 75L slab boundary ---
borrower_boundary = {
    "net_income": 300000,
    "existing_emis": 0,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 750,
}

result_at_boundary = lender_sanction(borrower_boundary, hdfc)
print("Property EXACTLY Rs 75,00,000 at HDFC:")
print("  Sanction:", result_at_boundary["sanction"], "| Binding:", result_at_boundary["binding"])

expected_at_boundary = round(7500000 * 0.80)
assert result_at_boundary["sanction"] == expected_at_boundary, \
    "At exactly 75L, expected 80% slab (" + str(expected_at_boundary) + "), got " + str(result_at_boundary["sanction"])

borrower_over = dict(borrower_boundary)
borrower_over["property_value"] = 7500001
result_over = lender_sanction(borrower_over, hdfc)
print("Property Rs 75,00,001 (one rupee over) at HDFC:")
print("  Sanction:", result_over["sanction"], "| Binding:", result_over["binding"])

expected_over = round(7500001 * 0.75)
assert result_over["sanction"] == expected_over, \
    "At 75L+1, expected 75% slab (" + str(expected_over) + "), got " + str(result_over["sanction"])
assert result_over["sanction"] < result_at_boundary["sanction"], \
    "One rupee over the boundary should produce a LOWER sanction (75% slab kicks in), not higher"

print()
print("Edge Case 3 (exact slab boundary) - PASSED")
print("  At 75L: Rs", format(result_at_boundary["sanction"], ","), "(80% slab) | At 75L+1: Rs",
      format(result_over["sanction"], ","), "(75% slab) -- one rupee costs Rs",
      format(result_at_boundary["sanction"] - result_over["sanction"], ","))

# --- Edge Case 4: property exactly at SBI's 20L boundary (2-slab shape) ---
with open("lenders/sbi.json") as f:
    sbi = json.load(f)

borrower_sbi_boundary = {
    "net_income": 300000,
    "existing_emis": 0,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 2000000,
    "cibil": 750,
}

result_sbi_at = lender_sanction(borrower_sbi_boundary, sbi)
print("Property EXACTLY Rs 20,00,000 at SBI:")
print("  Sanction:", result_sbi_at["sanction"], "| Binding:", result_sbi_at["binding"])

expected_sbi_at = round(2000000 * 0.90)
assert result_sbi_at["sanction"] == expected_sbi_at, \
    "At exactly 20L, expected 90% slab (" + str(expected_sbi_at) + "), got " + str(result_sbi_at["sanction"])

borrower_sbi_over = dict(borrower_sbi_boundary)
borrower_sbi_over["property_value"] = 2000001
result_sbi_over = lender_sanction(borrower_sbi_over, sbi)
print("Property Rs 20,00,001 (one rupee over) at SBI:")
print("  Sanction:", result_sbi_over["sanction"], "| Binding:", result_sbi_over["binding"])

expected_sbi_over = round(2000001 * 0.80)
assert result_sbi_over["sanction"] == expected_sbi_over, \
    "At 20L+1, expected 80% slab (" + str(expected_sbi_over) + "), got " + str(result_sbi_over["sanction"])
assert result_sbi_over["sanction"] < result_sbi_at["sanction"], \
    "One rupee over SBI's 20L boundary should drop to the 80% slab, producing a lower sanction"

print()
print("Edge Case 4 (SBI 2-slab boundary) - PASSED")
print("  At 20L: Rs", format(result_sbi_at["sanction"], ","), "(90% slab) | At 20L+1: Rs",
      format(result_sbi_over["sanction"], ","), "(80% slab)")

# --- Edge Case 5: CIBIL exactly at ICICI's hard floor (700) ---
with open("lenders/icici.json") as f:
    icici = json.load(f)

borrower_cibil_700 = {
    "net_income": 150000,
    "existing_emis": 0,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 700,
}

result_700 = lender_sanction(borrower_cibil_700, icici)
print("CIBIL exactly 700 at ICICI:")
print("  Binding:", result_700["binding"], "| Sanction:", result_700["sanction"])

assert result_700["binding"] != "DECLINE", "CIBIL exactly AT the floor (700) should NOT be declined - only strictly below"

borrower_cibil_699 = dict(borrower_cibil_700)
borrower_cibil_699["cibil"] = 699

result_699 = lender_sanction(borrower_cibil_699, icici)
print("CIBIL 699 (one point below) at ICICI:")
print("  Binding:", result_699["binding"], "| Sanction:", result_699["sanction"])

assert result_699["binding"] == "DECLINE", "CIBIL 699, one point below the floor, SHOULD decline"

print()
print("Edge Case 5 (CIBIL exact floor boundary) - PASSED")
print("  CIBIL 700: sanctioned | CIBIL 699: declined -- one point makes the difference")

# --- Edge Case 6: existing EMIs exceed FOIR allowance entirely ---
borrower_overloaded = {
    "net_income": 50000,
    "existing_emis": 40000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 750,
}

result_overloaded = lender_sanction(borrower_overloaded, hdfc)
print("Borrower with EMIs exceeding FOIR allowance at HDFC:")
print("  Sanction:", result_overloaded["sanction"], "| Binding:", result_overloaded["binding"])

assert result_overloaded["sanction"] == 0, "FOIR-exhausted borrower should get exactly Rs 0 sanction, got " + str(result_overloaded["sanction"])
assert result_overloaded["binding"] == "FOIR", "Should be FOIR-bound (the zero-ing-out constraint), got " + result_overloaded["binding"]

print()
print("Edge Case 6 (FOIR allowance exhausted by existing EMIs) - PASSED")
print("  Correctly returns Rs 0 sanction, no crash, no negative number")

# --- Edge Case 7: very high income buyer (Rs 5L+/month) ---
borrower_high_income = {
    "net_income": 500000,
    "existing_emis": 20000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 20000000,
    "cibil": 800,
}

result_high = lender_sanction(borrower_high_income, hdfc)
print("Rs 5,00,000/month income, Rs 2 crore property, at HDFC:")
print("  Sanction:", result_high["sanction"], "| Binding:", result_high["binding"])

expected_ltv = round(20000000 * 0.75)
assert result_high["binding"] == "LTV", "High-income buyer should be LTV-bound, not FOIR-bound, got " + result_high["binding"]
assert result_high["sanction"] == expected_ltv, "Expected LTV-capped sanction of " + str(expected_ltv) + ", got " + str(result_high["sanction"])

print()
print("Edge Case 7 (very high income, LTV always binds) - PASSED")
print("  Correctly LTV-bound at Rs", format(result_high["sanction"], ","), "-- FOIR never becomes the constraint at this income level")

# --- Edge Case 8: young borrower (age 25) - lender's max tenure caps, not age ---
borrower_young = {
    "net_income": 150000,
    "existing_emis": 0,
    "age": 25,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 750,
}

result_young = lender_sanction(borrower_young, hdfc)
print("Age 25 borrower at HDFC:")
print("  Sanction:", result_young["sanction"], "| Binding:", result_young["binding"], "| Tenure:", result_young["tenure_years"], "yrs")

assert result_young["tenure_years"] == 30, "Expected tenure capped at lender's own max (30 yrs), not borrower's theoretical 35 yrs, got " + str(result_young["tenure_years"])

print()
print("Edge Case 8 (young borrower, lender tenure cap binds) - PASSED")
print("  Correctly capped at HDFC's own 30-yr max, even though age alone would allow 35 yrs")

# --- Edge Case 9: low property value hits the 90% slab (untested tier so far) ---
borrower_low_value = {
    "net_income": 100000,
    "existing_emis": 0,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 1500000,
    "cibil": 750,
}

result_low = lender_sanction(borrower_low_value, hdfc)
print("Rs 15,00,000 property at HDFC:")
print("  Sanction:", result_low["sanction"], "| Binding:", result_low["binding"])

expected_low_ltv = round(1500000 * 0.90)
assert result_low["binding"] == "LTV", "Expected LTV-bound at this low property value/decent income, got " + result_low["binding"]
assert result_low["sanction"] == expected_low_ltv, "Expected 90% slab sanction of " + str(expected_low_ltv) + ", got " + str(result_low["sanction"])

print()
print("Edge Case 9 (low property value, 90% slab) - PASSED")
print("  Correctly sanctioned at Rs", format(result_low["sanction"], ","), "(90% of property value) - the cheapest LTV tier")

# --- Edge Case 10: employment_type "professional" at Bajaj (third rate tier) ---
with open("lenders/bajaj.json") as f:
    bajaj = json.load(f)

borrower_professional = {
    "net_income": 150000,
    "existing_emis": 0,
    "age": 34,
    "employment_type": "professional",
    "property_value": 7500000,
    "cibil": 750,
}

result_prof = lender_sanction(borrower_professional, bajaj)
print("Employment type 'professional' at Bajaj:")
print("  Rate:", round(result_prof["rate_pct"], 2), "% | Sanction:", result_prof["sanction"])

assert round(result_prof["rate_pct"], 2) == 7.30, "Expected professional_min rate of 7.30%, got " + str(round(result_prof["rate_pct"], 2))

borrower_salaried_bajaj = dict(borrower_professional)
borrower_salaried_bajaj["employment_type"] = "salaried"
result_sal_bajaj = lender_sanction(borrower_salaried_bajaj, bajaj)

borrower_se_bajaj = dict(borrower_professional)
borrower_se_bajaj["employment_type"] = "self_employed"
result_se_bajaj = lender_sanction(borrower_se_bajaj, bajaj)

print("  Compare -- salaried:", round(result_sal_bajaj["rate_pct"], 2), "% | self_employed:", round(result_se_bajaj["rate_pct"], 2), "% | professional:", round(result_prof["rate_pct"], 2), "%")

assert result_prof["rate_pct"] != result_sal_bajaj["rate_pct"], "Professional rate should differ from salaried rate at Bajaj"
assert result_prof["rate_pct"] != result_se_bajaj["rate_pct"], "Professional rate should differ from self_employed rate at Bajaj"

print()
print("Edge Case 10 (Bajaj three-way rate tier, professional) - PASSED")
print("  All three employment types correctly read distinct rate keys, none collapsed into another")

# --- Edge Case 11: multiple simultaneous flags don't overwrite each other ---
borrower_multi_flag = {
    "net_income": 150000,
    "existing_emis": 18000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 690,
}

result_multi = lender_sanction(borrower_multi_flag, hdfc)
print("HDFC, CIBIL 690 (below floor) - checking flag accumulation:")
for f in result_multi["flags"]:
    print("  -", f)

assert len(result_multi["flags"]) >= 2, "Expected at least 2 simultaneous flags (CIBIL caveat + FOIR default), got " + str(len(result_multi["flags"]))
assert any("soft gradient" in f for f in result_multi["flags"]), "Missing the CIBIL soft-gradient caveat flag"
assert any("FOIR cap ASSUMED" in f for f in result_multi["flags"]), "Missing the FOIR default flag"
assert result_multi["binding"] != "DECLINE", "Should still sanction despite the caveat - this is a soft gate, not a hard one"

print()
print("Edge Case 11 (multiple simultaneous flags) - PASSED")
print("  Both flags present and neither suppressed the other -", len(result_multi["flags"]), "total flags")

# --- Edge Case 12: shortfall exactly zero (not just close to zero) ---
with open("lenders/sbi.json") as f:
    sbi_case12 = json.load(f)

borrower_exact = {
    "net_income": 300000,
    "existing_emis": 0,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 2000000,
    "available_own_funds": 200000,
    "cibil": 750,
}

result_exact = lender_sanction(borrower_exact, sbi_case12)
loan_required_exact, shortfall_exact = compute_shortfall(borrower_exact, result_exact)
print("Borrower with shortfall EXACTLY zero at SBI:")
print("  Sanction:", result_exact["sanction"], "| Loan required:", loan_required_exact, "| Shortfall:", shortfall_exact)

assert shortfall_exact == 0, "Expected shortfall of exactly 0, got " + str(shortfall_exact)

fixes_exact = get_fixes(borrower_exact, sbi_case12, result_exact)
assert len(fixes_exact) == 0, "Expected ZERO fixes when shortfall is exactly 0, got " + str(len(fixes_exact))

print()
print("Edge Case 12 (shortfall exactly zero) - PASSED")
print("  Correctly returns zero fixes when sanction exactly meets the requirement, no false positive")

# --- Edge Case 13: declined lender produces zero fixes, no crash ---
with open("lenders/icici.json") as f:
    icici_case13 = json.load(f)

borrower_declined = {
    "net_income": 150000,
    "existing_emis": 18000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "available_own_funds": 500000,
    "cibil": 650,
}

result_declined = lender_sanction(borrower_declined, icici_case13)
print("ICICI, CIBIL 650 (well below floor):")
print("  Binding:", result_declined["binding"], "| Sanction:", result_declined["sanction"])

assert result_declined["binding"] == "DECLINE", "Expected a hard decline at CIBIL 650, got " + result_declined["binding"]

fixes_declined = get_fixes(borrower_declined, icici_case13, result_declined)
print("  Fixes suggested:", len(fixes_declined))

assert len(fixes_declined) == 0, "A declined lender should produce ZERO fixes - no crash, no nonsensical suggestions"

print()
print("Edge Case 13 (declined lender, zero fixes, no crash) - PASSED")
print("  Correctly returns an empty fix list for a hard decline, does not attempt to compute shortfall math on it")

# --- Edge Case 14: co-applicant field present but NOT used (documents a real gap) ---
borrower_with_coapplicant_field = {
    "net_income": 80000,
    "existing_emis": 15000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 6000000,
    "cibil": 750,
    "co_applicant_income": 60000,
}

result_coapp = lender_sanction(borrower_with_coapplicant_field, hdfc)
print("Borrower with unused co_applicant_income field at HDFC:")
print("  Sanction:", result_coapp["sanction"], "| Binding:", result_coapp["binding"])

borrower_without_coapplicant = dict(borrower_with_coapplicant_field)
del borrower_without_coapplicant["co_applicant_income"]
result_no_coapp = lender_sanction(borrower_without_coapplicant, hdfc)

assert result_coapp["sanction"] == result_no_coapp["sanction"], \
    "Co-applicant income should have NO effect currently (not yet implemented) - sanction changed unexpectedly"

print()
print("Edge Case 14 (co-applicant field present, correctly unused) - PASSED")
print("  KNOWN GAP: co-applicant income clubbing is not implemented - DSA-gated data required first")
print("  Confirmed: engine does not crash on the extra field, and does not silently half-apply it either")

# --- Edge Case 15: full pipeline integration - run_all_lenders end to end ---
from run_all_lenders import load_lenders, run_all_lenders, LENDER_FILES

lenders_case15 = load_lenders(LENDER_FILES)

borrower_integration = {
    "net_income": 150000,
    "existing_emis": 18000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "available_own_funds": 800000,
    "cibil": 690,
}

ranked_case15 = run_all_lenders(borrower_integration, lenders_case15)

print("Full pipeline run - lenders returned:", len(ranked_case15))
assert len(ranked_case15) == 6, "Expected all 6 lenders in the ranked output, got " + str(len(ranked_case15))

declined = [r for r in ranked_case15 if r["binding"] == "DECLINE"]
approved = [r for r in ranked_case15 if r["binding"] != "DECLINE"]
print("  Approved:", len(approved), "| Declined:", len(declined))
assert len(declined) == 1, "Expected exactly 1 decline (ICICI at CIBIL 690), got " + str(len(declined))
assert declined[0]["lender"] == "ICICI", "Expected ICICI to be the declined lender, got " + declined[0]["lender"]

sanctions_in_order = [r["sanction"] for r in approved]
assert sanctions_in_order == sorted(sanctions_in_order, reverse=True), "Approved lenders are not correctly ranked by sanction descending"

assert ranked_case15[-1]["binding"] == "DECLINE", "The declined lender should be last in the full ranked list"

for r in approved:
    assert "cash" in r, r["lender"] + " missing cash breakdown"
    assert "shortfall" in r, r["lender"] + " missing shortfall"
    assert "fixes" in r, r["lender"] + " missing fixes list"
    if r["shortfall"] > 0:
        assert isinstance(r["fixes"], list), r["lender"] + " fixes should be a list even if empty"

print()
print("Edge Case 15 (full pipeline integration) - PASSED")
print("  All 6 lenders present, correctly ranked, ICICI correctly declined and sorted last,")
print("  every approved lender carries cash/shortfall/fixes as expected")
print()
print("=" * 60)
print("ALL 15 EDGE CASES PASSED")
print("=" * 60)

print()
print("--- Edge Case 16: borrower already past retirement age ---")
past_retirement_borrower = {
    "net_income": 150000,
    "existing_emis": 15000,
    "age": 62,
    "employment_type": "salaried",
    "property_value": 7500000,
    "available_own_funds": 1500000,
}
hdfc = json.load(open("lenders/hdfc.json"))
result16 = lender_sanction(past_retirement_borrower, hdfc)
print("Age 62 (past HDFC's 60yo salaried retirement) at HDFC:")
print("  Sanction:", result16["sanction"], "| Binding:", result16["binding"])
print("  Flags:", result16["flags"])

assert result16["binding"] == "DECLINE", "Edge Case 16 FAILED: expected DECLINE, got " + result16["binding"]
assert result16["sanction"] == 0, "Edge Case 16 FAILED: expected 0 sanction, got " + str(result16["sanction"])
assert result16["sanction"] >= 0, "Edge Case 16 FAILED: sanction must never be negative"
print("Edge Case 16 (past-retirement-age decline) - PASSED")
print("  Correctly declines with zero sanction instead of silently computing a negative number")