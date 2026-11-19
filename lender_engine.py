from emi import foir_ceiling, max_tenure

DEFAULT_FOIR_CAP = 0.50

LTV_SLAB_SCHEMAS = [
    {
        "keys": {"upto_30L", "30L_to_75L", "above_75L"},
        "breakpoints": [(3000000, "upto_30L"), (7500000, "30L_to_75L")],
        "final": "above_75L",
    },
    {
        "keys": {"upto_20L", "above_20L"},
        "breakpoints": [(2000000, "upto_20L")],
        "final": "above_20L",
    },
]

def get_ltv_ceiling(property_value, ltv_slabs):
    keys = set(k for k in ltv_slabs.keys() if not k.startswith("_"))
    for schema in LTV_SLAB_SCHEMAS:
        if schema["keys"] == keys:
            for threshold, key in schema["breakpoints"]:
                if property_value <= threshold:
                    return property_value * ltv_slabs[key]
            return property_value * ltv_slabs[schema["final"]]
    raise KeyError("Unrecognized ltv_slabs shape: " + str(keys) + " - add a new schema to LTV_SLAB_SCHEMAS before wiring this lender")

def get_rate_pct(rate_band, employment_type, flags):
    confidence = rate_band.get("_confidence")
    if confidence in ("stale", "unknown", "partial"):
        flags.append("RATE " + str(confidence).upper() + " - source contested/unverified, re-check before quoting")

    if "effective_min" in rate_band:
        return rate_band["effective_min"] * 100

    key = employment_type + "_min"
    if key in rate_band:
        return rate_band[key] * 100

    if "salaried_min" in rate_band:
        flags.append("RATE - no '" + key + "' key found, fell back to salaried_min (verify manually for this employment type)")
        return rate_band["salaried_min"] * 100

    raise KeyError("No usable rate key found in rate_band for employment_type=" + employment_type)

def get_retirement_age(retirement_age_dict, employment_type, flags):
    if employment_type in retirement_age_dict:
        return retirement_age_dict[employment_type]

    if employment_type == "professional" and "self_employed" in retirement_age_dict:
        flags.append("RETIREMENT AGE - no 'professional' entry found, used 'self_employed' retirement age instead (lender does not split retirement age by professional status)")
        return retirement_age_dict["self_employed"]

    raise KeyError("No usable retirement_age entry found for employment_type=" + employment_type)

def lender_sanction(borrower, lender_json):
    flags = []

    rate_pct = get_rate_pct(lender_json["rate_band"], borrower["employment_type"], flags)

    cibil_data = lender_json.get("min_cibil", {})
    min_cibil = cibil_data.get("value")
    cibil_confidence = cibil_data.get("_confidence")

    if min_cibil is None and cibil_confidence == "unknown":
        aggregator_claim = cibil_data.get("aggregator_claim")
        if aggregator_claim:
            claim_parts = [k.replace("_", "-") + ": " + v for k, v in aggregator_claim.items()]
            claim_summary = "; ".join(claim_parts)
            flags.append("CIBIL requirement UNOFFICIAL for this lender - no official floor published. Unverified third-party range: " + claim_summary + ". Do not assume approval on CIBIL alone.")
        else:
            flags.append("CIBIL requirement UNKNOWN for this lender - no official floor published, unverified third-party claims exist. Do not assume approval on CIBIL alone.")

    if min_cibil is not None and "cibil" in borrower and borrower["cibil"] < min_cibil:
        if cibil_confidence == "verified":
            return {
                "lender": lender_json["lender"],
                "sanction": 0,
                "binding": "DECLINE",
                "rate_pct": rate_pct,
                "tenure_years": None,
                "flags": ["DECLINED - CIBIL " + str(borrower["cibil"]) + " below verified hard floor " + str(min_cibil)],
            }
        else:
            flags.append("CIBIL " + str(borrower["cibil"]) + " below stated " + str(min_cibil) + " (" + str(cibil_confidence) + " - soft gradient, not confirmed hard gate) - expect rate load or added scrutiny, not automatic decline")

    retirement = get_retirement_age(lender_json["retirement_age"], borrower["employment_type"], flags)
    years = max_tenure(borrower["age"], retirement, lender_json["max_tenure_years"]["value"])

    if years <= 0:
        return {
            "lender": lender_json["lender"],
            "sanction": 0,
            "binding": "DECLINE",
            "rate_pct": rate_pct,
            "tenure_years": None,
            "flags": ["DECLINED - borrower age " + str(borrower["age"]) + " is at or past this lender's retirement age (" + str(retirement) + ") for employment type " + borrower["employment_type"] + " - zero usable tenure"],
        }

    foir_data = lender_json["foir_by_income_band"]
    if foir_data.get("_confidence") == "unknown":
        foir_cap = DEFAULT_FOIR_CAP
        flags.append("FOIR cap ASSUMED " + str(DEFAULT_FOIR_CAP) + " - lender value not verified (DSA-gated)")
    else:
        foir_cap = foir_data["band_mid"]

    foir_amt = foir_ceiling(borrower["net_income"], borrower["existing_emis"], foir_cap, rate_pct, years)
    ltv_amt = get_ltv_ceiling(borrower["property_value"], lender_json["ltv_slabs"])

    final = min(foir_amt, ltv_amt)
    binding = "LTV" if final == ltv_amt else "FOIR"

    return {
        "lender": lender_json["lender"],
        "sanction": round(final),
        "binding": binding,
        "rate_pct": rate_pct,
        "tenure_years": years,
        "flags": flags,
    }