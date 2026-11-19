import json
from lender_engine import lender_sanction

with open("lenders/hdfc.json") as f:
    hdfc = json.load(f)
with open("lenders/icici.json") as f:
    icici = json.load(f)

borrower = {
    "net_income": 150000,
    "existing_emis": 18000,
    "age": 34,
    "employment_type": "salaried",
    "property_value": 7500000,
    "cibil": 690,
}

results = [lender_sanction(borrower, hdfc), lender_sanction(borrower, icici)]
results.sort(key=lambda r: r["sanction"], reverse=True)

for r in results:
    print("---", r["lender"], "---")
    for k, v in r.items():
        if k != "lender":
            print(" ", k, ":", v)