import os
import getpass
from extract_salary_slip import extract_from_document, is_safe_to_autofill

def ask_float(prompt, min_value=None, max_value=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("Please enter a number (e.g. 150000). You typed:", raw)
            continue
        if min_value is not None and value < min_value:
            print("Value must be at least", min_value, "- you entered", value)
            continue
        if max_value is not None and value > max_value:
            print("Value must be at most", max_value, "- you entered", value)
            continue
        return value

def ask_int(prompt, min_value=None, max_value=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number (e.g. 34). You typed:", raw)
            continue
        if min_value is not None and value < min_value:
            print("Value must be at least", min_value, "- you entered", value)
            continue
        if max_value is not None and value > max_value:
            print("Value must be at most", max_value, "- you entered", value)
            continue
        return value

def ask_choice(prompt, valid_choices):
    while True:
        raw = input(prompt).strip().lower()
        if raw in valid_choices:
            return raw
        print("Please enter one of:", ", ".join(valid_choices), "- you typed:", raw)

def ask_optional_int(prompt, min_value=None, max_value=None):
    raw = input(prompt).strip()
    if raw == "":
        return None
    try:
        value = int(raw)
    except ValueError:
        print("Not a valid number, treating CIBIL as not provided.")
        return None
    if min_value is not None and value < min_value:
        print("CIBIL must be at least", min_value, "- treating as not provided since", value, "is not a real score.")
        return None
    if max_value is not None and value > max_value:
        print("CIBIL must be at most", max_value, "- treating as not provided since", value, "is not a real score.")
        return None
    return value

def get_api_key():
    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        return env_key
    return getpass.getpass("Paste your Anthropic API key (input hidden): ").strip()

def get_net_income():
    print("Paste salary slip text (or press Enter to skip and enter income manually):")
    slip_text = input().strip()

    if slip_text == "":
        return ask_float("Net monthly income (Rs): ", min_value=1)

    api_key = get_api_key()

    try:
        extracted, notes = extract_from_document(slip_text, api_key)
    except Exception as e:
        print("Extraction failed:", e)
        print("Falling back to manual entry.")
        return ask_float("Net monthly income (Rs): ", min_value=1)

    print()
    print("--- Extracted from document ---")
    print("Net income:", extracted.get("net_income"))
    print("Confidence:", extracted.get("confidence", {}).get("net_income"))
    if notes:
        print("Notes:", notes)
    if extracted.get("extraction_notes"):
        print("Model notes:", extracted.get("extraction_notes"))
    print()

    net_income = extracted.get("net_income")

    if is_safe_to_autofill(extracted):
        raw = input("Press Enter to accept Rs " + str(net_income) + ", or type a different number: ").strip()
        if raw == "":
            return float(net_income)
        try:
            return float(raw)
        except ValueError:
            print("Not a valid number, please enter it manually.")
            return ask_float("Net monthly income (Rs): ", min_value=1)
    else:
        print("Extraction confidence was not high enough to auto-fill - please confirm manually.")
        if net_income is not None:
            print("(Extracted value was Rs " + str(net_income) + ", shown as reference only)")
        return ask_float("Net monthly income (Rs): ", min_value=1)

def collect_borrower():
    print("--- Enter borrower details ---")
    net_income = get_net_income()
    existing_emis = ask_float("Existing monthly EMI outflow (Rs, 0 if none): ", min_value=0)
    age = ask_int("Borrower age (years): ", min_value=18, max_value=75)
    employment_type = ask_choice(
        "Employment type (salaried / self_employed / professional): ",
        ["salaried", "self_employed", "professional"],
    )
    property_value = ask_float("Property value (Rs): ", min_value=1)
    available_own_funds = ask_float("Own funds available for down payment + costs (Rs): ", min_value=0)
    cibil = ask_optional_int("CIBIL score (leave blank if not known): ", min_value=300, max_value=900)

    borrower = {
        "net_income": net_income,
        "existing_emis": existing_emis,
        "age": age,
        "employment_type": employment_type,
        "property_value": property_value,
        "available_own_funds": available_own_funds,
    }
    if cibil is not None:
        borrower["cibil"] = cibil

    return borrower