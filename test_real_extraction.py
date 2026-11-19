from extract_salary_slip import extract_from_document

SAMPLE_SALARY_SLIP = """
EXAMPLE CORP PVT LTD
Payslip for July 2026

Employee Name: Rahul Sharma
Employee ID: EC-4821

EARNINGS
Basic Salary:        Rs 85,000
HRA:                  Rs 42,500
Special Allowance:    Rs 57,500
Gross Salary:         Rs 1,85,000

DEDUCTIONS
Provident Fund:       Rs 10,200
Professional Tax:     Rs 200
Income Tax (TDS):     Rs 22,600
Total Deductions:     Rs 33,000

NET SALARY (TAKE HOME): Rs 1,52,000
"""

api_key = input("Paste your Anthropic API key: ").strip()

extracted, notes = extract_from_document(SAMPLE_SALARY_SLIP, api_key)

print()
print("--- Extracted data ---")
print(extracted)
print()
print("--- Validation notes ---")
print(notes)