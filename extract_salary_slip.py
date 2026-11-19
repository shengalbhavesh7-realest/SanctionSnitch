import json

EXTRACTION_PROMPT = """Extract the following fields from this salary slip and return ONLY valid JSON, no other text:

{
  "gross_income": <number, monthly gross salary before deductions>,
  "net_income": <number, monthly take-home / net salary>,
  "deductions": <number, total deductions>,
  "employer_name": <string>,
  "pay_month": <string, e.g. "July 2026">,
  "confidence": {
    "gross_income": "high" | "medium" | "low",
    "net_income": "high" | "medium" | "low",
    "deductions": "high" | "medium" | "low",
    "employer_name": "high" | "medium" | "low",
    "pay_month": "high" | "medium" | "low"
  },
  "extraction_notes": <string, any ambiguity or issue you noticed, empty string if none>
}

If a field cannot be determined, use null for its value and "low" for its confidence.
Confidence should reflect how clearly the document states this value - "high" only if the
number is printed plainly and unambiguously, "low" if you had to infer or guess."""


def validate_extraction(extracted):
    notes = []

    gross = extracted.get("gross_income")
    net = extracted.get("net_income")
    deductions = extracted.get("deductions")

    if gross is not None and net is not None and deductions is not None:
        expected_net = gross - deductions
        if abs(expected_net - net) > 100:
            notes.append(
                "MATH MISMATCH: gross (" + str(gross) + ") - deductions (" + str(deductions) +
                ") = " + str(expected_net) + ", but extracted net_income is " + str(net) +
                ". Forcing net_income confidence to LOW regardless of model's self-report."
            )
            extracted["confidence"]["net_income"] = "low"

    return extracted, notes


def is_safe_to_autofill(extracted, field="net_income"):
    confidence = extracted.get("confidence", {}).get(field)
    value = extracted.get(field)
    return confidence == "high" and value is not None


def extract_from_document(document_text, api_key):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT + "\n\n---DOCUMENT---\n" + document_text}
        ]
    )
    raw_text = None
    for block in message.content:
       if block.type == "text":
           raw_text = block.text
           break

    if raw_text is None:
        raise ValueError("No text block found in the API response - only got: " + str([b.type for b in message.content]))
    print("--- RAW MODEL RESPONSE ---")
    print(raw_text)
    print("--- END RAW RESPONSE ---")

    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```"):
        lines = cleaned_text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned_text = "\n".join(lines)

    extracted = json.loads(cleaned_text)
    extracted, notes = validate_extraction(extracted)
    return extracted, notes