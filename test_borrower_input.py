from borrower_input import collect_borrower

borrower = collect_borrower()
print()
print("--- Collected borrower dict ---")
print(borrower)
print()
print("Type check:")
print("net_income is float:", isinstance(borrower["net_income"], float))
print("age is int:", isinstance(borrower["age"], int))
print("employment_type is str:", isinstance(borrower["employment_type"], str))