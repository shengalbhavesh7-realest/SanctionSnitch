from emi import sanction, max_tenure, foir_ceiling, ltv_ceiling, multiple_ceiling

import json
import os

lender_files = ["hdfc", "icici", "sbi", "axis", "bajaj", "lichfl"]

lenders = {}
for name in lender_files:
	path = os.path.join("lenders", name + ".json")
	with open(path) as f:
		lenders[name] = json.load(f)

print("Loaded", len(lenders), "lenders:")
for name, data in lenders.items():
	print(" -", data["lender"])

print("\n--- Field check: does every lender have the engine-critical fields? ---")

critical_fields = ["ltv_slabs", "max_tenure_years", "retirement_age",
                   "min_cibil", "rate_band", "foir_by_income_band",
                   "accepted_income_proofs", "co_applicant_clubbing"]

for name, data in lenders.items():
    missing = []
    for field in critical_fields:
        if field not in data:
            missing.append(field)
    if missing:
        print(data["lender"], "MISSING:", missing)
    else:
        print(data["lender"], "- all fields present")

print("\n--- Prime rate comparison (the arbitrage, live) ---")

for name, data in lenders.items():
    rate = data["rate_band"]
    # different lenders store the rate differently, so check what exists
    if "effective_min" in rate:
        print(data["lender"], "prime rate:", rate["effective_min"])
    elif "salaried_min" in rate:
        print(data["lender"], "prime rate:", rate["salaried_min"])
    else:
        print(data["lender"], "prime rate: (stored differently)")