from extract_salary_slip import extract_from_document

MESSY_SALARY_SLIP = """
QUICKSERVE TECHNOLOGIES
Salary Statement - Month: 07/2026

Name: A. Krishnan
Emp Code: QT2291

Pay Components (Monthly)
Basic                 78000
HRA                   39000
Conveyance             1600
Medical                1250
Special Pay          ~41000 (variable, subject to attendance)

Gross                160850 (approx, pending final attendance adjustment)

Deductions
PF                     9360
Prof Tax                200
TDS                  ~18000

Take home credited to account: around 1,33,000 (may vary slightly month to month)
"""

api_key = input("Paste your Anthropic API key: ").strip()

extracted, notes = extract_from_document(MESSY_SALARY_SLIP, api_key)

print()
print("--- Extracted data ---")
print(extracted)
print()
print("--- Validation notes ---")
print(notes)