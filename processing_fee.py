EMPLOYMENT_TYPE_TO_FEE_KEY = {
    "salaried": "salaried",
    "professional": "self_employed_professional",
    "self_employed": "self_employed_non_professional",  # ASSUMPTION - see flag below
}

def get_processing_fee(processing_fee_json, sanction_amount, employment_type, flags):
    if processing_fee_json is None:
        return None

    # Shape 1: flat top-level pct (ICICI, Axis)
    if "pct" in processing_fee_json:
        pct = processing_fee_json["pct"]
        min_flat = processing_fee_json.get("min_flat", 0)
        return round(max(sanction_amount * pct, min_flat))

    # Shape 3: SBI-style tiered by LOAN SIZE, not employment type
    if "upto_25L_pct" in processing_fee_json:
        if sanction_amount <= 2500000:
            return round(sanction_amount * processing_fee_json["upto_25L_pct"])
        elif sanction_amount <= 7500000:
            return processing_fee_json["25L_to_75L_flat"]
        else:
            return processing_fee_json["above_75L_flat"]

    # Shape 4: Bajaj-style range, no single confident number
    if "pct_min" in processing_fee_json:
        low = round(sanction_amount * processing_fee_json["pct_min"])
        high = round(sanction_amount * processing_fee_json["pct_absolute_max"])
        flags.append("PROCESSING FEE is a RANGE for this lender (Rs " + format(low, ",") +
                      " to Rs " + format(high, ",") + ") - varies by risk profile, no single figure available")
        return None  # no single number - the flag carries the real information

    # Shape 2: nested by employment type (HDFC, LIC HFL)
    fee_key = EMPLOYMENT_TYPE_TO_FEE_KEY.get(employment_type)
    if fee_key and fee_key in processing_fee_json:
        if employment_type == "self_employed":
            flags.append("PROCESSING FEE assumed 'non-professional' self-employed rate - borrower profile does not specify professional status")
        fee_data = processing_fee_json[fee_key]
        pct = fee_data["pct"]
        min_flat = fee_data.get("min_flat", 0)
        return round(max(sanction_amount * pct, min_flat))

    flags.append("PROCESSING FEE - unrecognized schema for this lender, not included in cash breakdown")
    return None