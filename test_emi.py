from emi import (
    emi,
    max_principal,
    schedule,
    foir_ceiling,
    max_tenure,
    ltv_ceiling,
    multiple_ceiling,
    sanction,
    cash_needed,
)

e = emi(5000000, 8.5, 20)
print("EMI:", round(e))
print("Back to principal:", round(max_principal(e, 8.5, 20)))

for p, rate, yrs in [(7500000, 9.0, 25), (3000000, 8.0, 15), (10000000, 9.5, 30)]:
    e2 = emi(p, rate, yrs)
    back = max_principal(e2, rate, yrs)
    print(p, "->", round(e2), "->", round(back))

rows = schedule(5000000, 8.5, 20)
print("Month 1:", rows[0])
print("Interest share of first EMI:", round(rows[0][1] / e * 100, 1), "%")

for row in rows:
    if row[2] > row[1]:
        print("principal exceeds interest at month:", row[0])
        break

print("FOIR ceiling:", round(foir_ceiling(150000, 18000, 0.50, 8.5, 26)))

print("Max tenure:", max_tenure(34, 60, 30))
print("LTV, valuation = price:", round(ltv_ceiling(7500000, 7500000)))
print("LTV, valuation 8% low:", round(ltv_ceiling(7500000, 6900000)))

amount, binding = sanction(150000, 18000, 0.50, 34, 60, 30, 7500000, 7500000, 8.5, 6)
print("sanction:", amount, "| Binding:", binding)

for price in [5000000, 6000000, 7000000, 7500000, 8500000]:
    amt, b = sanction(150000, 18000, 0.50, 34, 60, 30, price, price, 8.5, 6)
    print(price, "->", amt, "|", b)

print("--- weaker income buyer ---")
for price in [3000000, 4000000, 5000000, 6000000]:
    amt, b = sanction(80000, 25000, 0.50, 34, 60, 30, price, price, 8.5, 6)
    print(price, "->", amt, "|", b)

print("multiple ceiling:", round(multiple_ceiling(150000, 6)))

gap = cash_needed(7500000, 6000000, 0.06, 0.01, 30000, 21000, 0.0)

print("--- cash breakdown ---")
for item, amount in gap.items():
    print(item, ":", amount)