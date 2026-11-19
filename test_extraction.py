from extract_salary_slip import validate_extraction, is_safe_to_autofill

print("--- Test 1: clean extraction, math reconciles, high confidence -> safe to autofill ---")
clean_extraction = {
    "gross_income": 185000,
    "net_income": 152000,
    "deductions": 33000,
    "employer_name": "Example Corp Pvt Ltd",
    "pay_month": "July 2026",
    "confidence": {
        "gross_income": "high",
        "net_income": "high",
        "deductions": "high",
        "employer_name": "high",
        "pay_month": "high"
    },
    "extraction_notes": ""
}
result, notes = validate_extraction(clean_extraction)
print("Notes:", notes)
print("Safe to autofill net_income?", is_safe_to_autofill(result))
assert is_safe_to_autofill(result) == True
assert len(notes) == 0

print()
print("--- Test 2: model claims high confidence, but math DOESN'T reconcile -> forced to low, blocked ---")
bad_math_extraction = {
    "gross_income": 185000,
    "net_income": 170000,
    "deductions": 33000,
    "employer_name": "Example Corp Pvt Ltd",
    "pay_month": "July 2026",
    "confidence": {
        "gross_income": "high",
        "net_income": "high",
        "deductions": "high",
        "employer_name": "high",
        "pay_month": "high"
    },
    "extraction_notes": ""
}
result2, notes2 = validate_extraction(bad_math_extraction)
print("Notes:", notes2)
print("Confidence after validation:", result2["confidence"]["net_income"])
print("Safe to autofill net_income?", is_safe_to_autofill(result2))
assert result2["confidence"]["net_income"] == "low"
assert is_safe_to_autofill(result2) == False
assert len(notes2) == 1

print()
print("--- Test 3: model honestly reports low/medium confidence -> correctly blocked, no math issue ---")
low_confidence_extraction = {
    "gross_income": 185000,
    "net_income": 152000,
    "deductions": 33000,
    "employer_name": "Example Corp Pvt Ltd",
    "pay_month": "July 2026",
    "confidence": {
        "gross_income": "high",
        "net_income": "medium",
        "deductions": "high",
        "employer_name": "high",
        "pay_month": "high"
    },
    "extraction_notes": "Net income figure was slightly smudged/unclear in the scan"
}
result3, notes3 = validate_extraction(low_confidence_extraction)
print("Safe to autofill net_income?", is_safe_to_autofill(result3))
assert is_safe_to_autofill(result3) == False

print()
print("--- Test 4: missing/null field -> correctly blocked, no crash ---")
missing_field_extraction = {
    "gross_income": 185000,
    "net_income": None,
    "deductions": None,
    "employer_name": "Example Corp Pvt Ltd",
    "pay_month": "July 2026",
    "confidence": {
        "gross_income": "high",
        "net_income": "low",
        "deductions": "low",
        "employer_name": "high",
        "pay_month": "high"
    },
    "extraction_notes": "Net income section was cut off in the document"
}
result4, notes4 = validate_extraction(missing_field_extraction)
print("Safe to autofill net_income?", is_safe_to_autofill(result4))
assert is_safe_to_autofill(result4) == False

print()
print("ALL EXTRACTION VALIDATION TESTS PASSED")