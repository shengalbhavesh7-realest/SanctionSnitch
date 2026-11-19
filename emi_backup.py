def emi(P, annual_rate, years):
	r=annual_rate/12/100
	n=years*12
	factor=(1+r)**n
	return P*r*factor/(factor-1)

def max_principal(monthly_emi, annual_rate, years): 
	r=annual_rate/12/100
	n=years*12
	factor=(1+r)**n
	return monthly_emi*(factor-1)/(r*factor)

e=emi(5000000, 8.5, 20)
print("EMI:", round(e))
print("Back to principal:", round(max_principal(e, 8.5, 20)))

for p, rate, yrs in [(7500000, 9.0, 25), (3000000, 8.0, 15), (10000000, 9.5, 30)]: 
	e2= emi(p, rate, yrs)
	back= max_principal(e2, rate, yrs)
	print(p, "->", round(e2), "->", round(back))

def schedule(P, annual_rate, years):
	r= annual_rate/12/100
	n= years*12
	pay= emi(P, annual_rate, years)
	balance= P
	rows= []
	for month in range(1, n+1):
		interest= balance*r
		principal= pay-interest
		balance= balance-principal
		rows.append((month, round(interest), round(principal), round(balance)))
	return rows

rows= schedule(5000000, 8.5, 20)
print("Month 1:", rows[0])
print("Interest share of first EMI:", round(rows[0][1]/e*100, 1),"%")

for row in rows:
	if row[2] > row[1]: 
		print("prinicpal exceeds interest at month:", row[0])
		break

def foir_ceiling(net_monthly_income, existing_emis, foir_cap, annual_rate, years):
	allowed_total= net_monthly_income*foir_cap
	available_emi= allowed_total-existing_emis
	if available_emi <= 0:
		return 0
	return max_principal(available_emi, annual_rate, years)

print("FOIR ceiling:",round(foir_ceiling(150000, 18000, 0.50, 8.5, 26)))

def max_tenure(current_age, retirement_age, lender_max_tenure):
	years_to_retirement= retirement_age - current_age
	return min(years_to_retirement, lender_max_tenure)

def ltv_ceiling(property_value, lender_valuation):
	value= min(property_value, lender_valuation)
	if value<= 3000000:
		ltv= 0.90
	elif value <= 7500000:
		ltv= 0.80
	else: 
		ltv= 0.75
	return value*ltv

print("Max tenure:", max_tenure(34, 60, 30))
print("LTV, valuation = price:", round(ltv_ceiling(7500000, 7500000)))
print("LTV, valuation 8% low:", round(ltv_ceiling(7500000, 6900000)))

def multiple_ceiling(net_monthly_income, income_multiple):
	annual_income = net_monthly_income * 12
	return annual_income * income_multiple

def sanction(net_income, existing_emis, foir_cap, age, retirement_age, lender_max_tenure, property_value, lender_valuation, annual_rate, income_multiple):
	years= max_tenure(age, retirement_age, lender_max_tenure)
	foir_amt= foir_ceiling(net_income, existing_emis, foir_cap, annual_rate, years)
	ltv_amt= ltv_ceiling(property_value, lender_valuation)
	mult_amt= multiple_ceiling(net_income, income_multiple)
	final= min(foir_amt, ltv_amt, mult_amt)
	if final== ltv_amt:
		binding= "LTV"
	elif final == foir_amt:
		binding= "FOIR"
	else: 
		binding= "MULTIPLE"
	return round(final), binding



amount, binding= sanction(150000, 18000, 0.50, 34, 60, 30, 7500000, 7500000, 8.5, 6)
print("sanction:", amount,"| Binding:", binding)

for price in [5000000, 6000000, 7000000, 7500000, 8500000]:
	amt, b= sanction(150000, 18000, 0.50, 34, 60, 30, price, price, 8.5, 6)
	print(price,"->", amt, "|", b)

print("--- weaker income buyer ---")
for price in [3000000, 4000000, 5000000, 6000000]:
	amt, b = sanction(80000, 25000, 0.50, 34, 60, 30, price, price, 8.5, 6)
	print(price,"->", amt, "|", b)

print("multiple ceiling:", round(multiple_ceiling(150000, 6)))

def cash_needed(property_value, sanction_amount, stamp_duty_pct, registration_pct, registration_cap, processing_pct, gst_pct):
	down_payment = property_value - sanction_amount
	stamp_duty = property_value * stamp_duty_pct
	registration = min(property_value * registration_pct, registration_cap)
	processing = sanction_amount * processing_pct
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

gap = cash_needed(7500000, 6000000, 0.06, 0.01, 30000, 0.0035, 0.0)
print("--- cash breakdown ---")
for item, amount in gap.items():
	print(item, ":", amount)