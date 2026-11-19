import sys
import json
from emi import cash_needed
from lender_engine import lender_sanction
from fix_engine import get_fixes, compute_shortfall
from processing_fee import get_processing_fee
from borrower_input import collect_borrower

LENDER_FILES = [
    "lenders/hdfc.json",
    "lenders/icici.json",
    "lenders/axis.json",
    "lenders/bajaj.json",
    "lenders/lichfl.json",
    "lenders/sbi.json",
]

DEFAULT_STAMP_DUTY_PCT = 0.06
DEFAULT_REGISTRATION_PCT = 0.01
DEFAULT_REGISTRATION_CAP = 30000
DEFAULT_GST_PCT = 0.0

def load_lenders(filenames):
    lenders = []
    for filename in filenames:
        try:
            with open(filename) as f:
                lenders.append(json.load(f))
        except FileNotFoundError:
            print("WARNING: lender file not found, skipping:", filename)
        except json.JSONDecodeError as e:
            print("WARNING: lender file has invalid JSON, skipping:", filename, "-", e)
    if not lenders:
        print("ERROR: no lender files could be loaded. Check the lenders/ folder.")
    return lenders

def run_all_lenders(borrower, lender_jsons):
    results = []
    for lender_json in lender_jsons:
        try:
            result = lender_sanction(borrower, lender_json)
        except KeyError as e:
            print("WARNING: lender data missing required field", e, "for", lender_json.get("lender", "unknown lender"), "- skipping this lender")
            continue

        if result["binding"] != "DECLINE":
            processing_fee_json = lender_json.get("processing_fee")
            processing_fee_amount = get_processing_fee(
                processing_fee_json,
                result["sanction"],
                borrower["employment_type"],
                result["flags"],
            )
            result["processing_fee_amount"] = processing_fee_amount

            cash = cash_needed(
                borrower["property_value"],
                result["sanction"],
                DEFAULT_STAMP_DUTY_PCT,
                DEFAULT_REGISTRATION_PCT,
                DEFAULT_REGISTRATION_CAP,
                processing_fee_amount,
                DEFAULT_GST_PCT,
            )
            result["cash"] = cash

            loan_required, shortfall = compute_shortfall(borrower, result)
            result["loan_required"] = loan_required
            result["shortfall"] = shortfall
            result["fixes"] = get_fixes(borrower, lender_json, result)

        results.append(result)

    declined = [r for r in results if r["binding"] == "DECLINE"]
    approved = [r for r in results if r["binding"] != "DECLINE"]
    approved.sort(key=lambda r: (-r["sanction"], r["rate_pct"]))

    return approved + declined

def print_report(borrower, ranked_results):
    print("=" * 60)
    print("BORROWER: income", borrower["net_income"], "| EMIs", borrower["existing_emis"],
          "| age", borrower["age"], "| CIBIL", borrower.get("cibil", "not provided"),
          "| property", borrower["property_value"],
          "| own funds", borrower.get("available_own_funds", 0))
    print("ASSUMPTION: stamp duty", DEFAULT_STAMP_DUTY_PCT * 100, "% | registration",
          DEFAULT_REGISTRATION_PCT * 100, "% capped at Rs", DEFAULT_REGISTRATION_CAP,
          "(Maharashtra-typical - verify for buyer's actual state)")
    print("=" * 60)
    for i, r in enumerate(ranked_results, 1):
        print(str(i) + ". " + r["lender"])
        if r["binding"] == "DECLINE":
            print("   DECLINED")
        else:
            print("   Sanction: Rs", format(r["sanction"], ","), "| Binding:", r["binding"],
                  "| Rate:", round(r["rate_pct"], 2), "%", "| Tenure:", r["tenure_years"], "yrs")
            c = r["cash"]

            if r["processing_fee_amount"] is None:
                print("   Cash needed to close (processing fee NOT included - see flag below): Rs", format(c["total_cash"], ","))
                print("     - processing fee: NOT AVAILABLE - single figure unknown, see flag")
            else:
                print("   Cash needed to close (incl. processing fee): Rs", format(c["total_cash"], ","))
                print("     - processing fee component: Rs", format(c["processing"], ","))

            if r["shortfall"] > 0:
                print("   SHORTFALL: Rs", format(r["shortfall"], ","), "vs Rs", format(r["loan_required"], ","), "required")
                if r["fixes"]:
                    print("   Ranked fixes:")
                    for f in r["fixes"]:
                        print("     - " + f["fix"] + " | impact Rs " + format(f["impact_rs"], ",") +
                              " (closes " + str(f["closes_shortfall_pct"]) + "% of shortfall)")
                else:
                    print("   No computable fix - may need co-applicant clubbing (DSA-gated, impact not quantified)")
            else:
                print("   No shortfall - sanction covers the required loan amount")
        for flag in r["flags"]:
            print("   - " + flag)
        print()

def run_demo():
    lenders = load_lenders(LENDER_FILES)

    print("### SCENARIO 1: buyer has normal 20% down payment saved - expect ZERO shortfall ###")
    normal_borrower = {
        "net_income": 150000,
        "existing_emis": 18000,
        "age": 34,
        "employment_type": "salaried",
        "property_value": 7500000,
        "available_own_funds": 1500000,
        "cibil": 690,
    }
    ranked1 = run_all_lenders(normal_borrower, lenders)
    print_report(normal_borrower, ranked1)

    print()
    print("### SCENARIO 2: buyer has only Rs 8L saved - genuine cash gap beyond down payment ###")
    short_borrower = dict(normal_borrower)
    short_borrower["available_own_funds"] = 800000
    ranked2 = run_all_lenders(short_borrower, lenders)
    print_report(short_borrower, ranked2)

def run_live():
    lenders = load_lenders(LENDER_FILES)
    borrower = collect_borrower()
    print()
    ranked = run_all_lenders(borrower, lenders)
    print_report(borrower, ranked)

if __name__ == "__main__":
    if "--live" in sys.argv:
        run_live()
    else:
        run_demo()