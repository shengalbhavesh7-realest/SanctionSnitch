from processing_fee import get_processing_fee

def check(name, result, expected):
    status = "PASS" if result == expected else "FAIL"
    print(status + " - " + name + " | got:", result, "| expected:", expected)

# 1. ICICI - flat pct, no min_flat
flags = []
result = get_processing_fee({"pct": 0.005}, 5000000, "salaried", flags)
check("ICICI flat pct", result, 25000)

# 2. Axis - flat pct with min_flat kicking in
flags = []
result = get_processing_fee({"pct": 0.005, "min_flat": 15000}, 1000000, "salaried", flags)
check("Axis flat pct + min_flat", result, 15000)

# 3. SBI - upto 25L tier
flags = []
result = get_processing_fee({"upto_25L_pct": 0.005, "25L_to_75L_flat": 10000, "above_75L_flat": 15000}, 2000000, "salaried", flags)
check("SBI upto_25L tier", result, 10000)

# 4. SBI - above 75L tier
flags = []
result = get_processing_fee({"upto_25L_pct": 0.005, "25L_to_75L_flat": 10000, "above_75L_flat": 15000}, 8000000, "salaried", flags)
check("SBI above_75L tier", result, 15000)

# 5. HDFC - salaried
flags = []
result = get_processing_fee({"salaried": {"pct": 0.005, "min_flat": 3000}, "self_employed_professional": {"pct": 0.01}, "self_employed_non_professional": {"pct": 0.015}}, 5000000, "salaried", flags)
check("HDFC salaried", result, 25000)

# 6. HDFC - self_employed (should fire assumption flag)
flags = []
result = get_processing_fee({"salaried": {"pct": 0.005}, "self_employed_professional": {"pct": 0.01}, "self_employed_non_professional": {"pct": 0.015}}, 5000000, "self_employed", flags)
check("HDFC self_employed", result, 75000)
check("HDFC self_employed assumption flag fired", len(flags) == 1, True)

# 7. HDFC - professional (no flag, unambiguous)
flags = []
result = get_processing_fee({"salaried": {"pct": 0.005}, "self_employed_professional": {"pct": 0.01}, "self_employed_non_professional": {"pct": 0.015}}, 5000000, "professional", flags)
check("HDFC professional", result, 50000)
check("HDFC professional no flag", len(flags) == 0, True)

# 8. Bajaj - range, no single number
flags = []
result = get_processing_fee({"pct_min": 0.0025, "pct_absolute_max": 0.04}, 6000000, "salaried", flags)
check("Bajaj range returns None", result, None)
check("Bajaj range flag fired", len(flags) == 1, True)

print()
print("All checks complete.")