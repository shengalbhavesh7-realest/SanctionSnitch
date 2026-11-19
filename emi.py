def emi(P, annual_rate, years):
    r = annual_rate / 12 / 100
    n = years * 12
    factor = (1 + r) ** n
    return P * r * factor / (factor - 1)

def max_principal(monthly_emi, annual_rate, years):
    r = annual_rate / 12 / 100
    n = years * 12
    factor = (1 + r) ** n
    return monthly_emi * (factor - 1) / (r * factor)

def schedule(P, annual_rate, years):
    r = annual_rate / 12 / 100
    n = years * 12
    pay = emi(P, annual_rate, years)
    balance = P
    rows = []
    for month in range(1, n + 1):
        interest = balance * r
        principal = pay - interest
        balance = balance - principal
        rows.append((month, round(interest), round(principal), round(balance)))
    return rows

def foir_ceiling(net_monthly_income, existing_emis, foir_cap, annual_rate, years):
    allowed_total = net_monthly_income * foir_cap
    available_emi = allowed_total - existing_emis
    if available_emi <= 0:
        return 0
    return max_principal(available_emi, annual_rate, years)

def max_tenure(current_age, retirement_age, lender_max_tenure):
    years_to_retirement = retirement_age - current_age
    return min(years_to_retirement, lender_max_tenure)

def ltv_ceiling(property_value, lender_valuation):
    value = min(property_value, lender_valuation)
    if value <= 3000000:
        ltv = 0.90
    elif value <= 7500000:
        ltv = 0.80
    else:
        ltv = 0.75
    return value * ltv

def multiple_ceiling(net_monthly_income, income_multiple):
    annual_income = net_monthly_income * 12
    return annual_income * income_multiple

def sanction(net_income, existing_emis, foir_cap, age, retirement_age, lender_max_tenure, property_value, lender_valuation, annual_rate, income_multiple):
    years = max_tenure(age, retirement_age, lender_max_tenure)
    foir_amt = foir_ceiling(net_income, existing_emis, foir_cap, annual_rate, years)
    ltv_amt = ltv_ceiling(property_value, lender_valuation)
    mult_amt = multiple_ceiling(net_income, income_multiple)
    final = min(foir_amt, ltv_amt, mult_amt)
    if final == ltv_amt:
        binding = "LTV"
    elif final == foir_amt:
        binding = "FOIR"
    else:
        binding = "MULTIPLE"
    return round(final), binding

def cash_needed(property_value, sanction_amount, stamp_duty_pct, registration_pct, registration_cap, processing_fee_amount, gst_pct):
       down_payment = property_value - sanction_amount
       stamp_duty = property_value * stamp_duty_pct
       registration = min(property_value * registration_pct, registration_cap)
       processing = processing_fee_amount if processing_fee_amount is not None else 0
       gst = property_value * gst_pct
       total = down_payment + stamp_duty + registration + processing + gst
       return {
           "down_payment": round(down_payment),
           "stamp_duty": round(stamp_duty),
           "registration": round(registration),
           "processing": round(processing),
           "gst": round(gst),
           "total_cash": round(total)
       }