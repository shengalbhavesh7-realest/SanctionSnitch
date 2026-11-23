import copy
import glob
import json
import os
from dotenv import load_dotenv

load_dotenv()


def _lender_key(name: str) -> str:
    n = name.lower()
    for token in ("hdfc", "icici", "axis", "bajaj", "lic", "sbi"):
        if token in n:
            return token
    return n.strip()


def load_local_policies(folder: str = "lenders") -> list[dict]:
    """Loads local JSON policy files (used both as base templates and offline fallback)."""
    search_root = folder if os.path.isdir(folder) else "."
    policies = []
    for path in sorted(glob.glob(os.path.join(search_root, "**", "*.json"), recursive=True)):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "lender" in data and "ltv_slabs" in data:
                data["_source"] = "local_json"
                policies.append(data)
    return policies


def _map_supabase_row_to_policy(row: dict, base_templates: dict[str, dict]) -> dict:
    """Overlays live Supabase lending_rules columns onto the lender's base JSON schema."""
    policy = copy.deepcopy(base_templates.get(_lender_key(row["lender_name"]), {}))
    confidence = str(row.get("confidence_tag") or "baseline").strip().lower()
    cibil_val = row.get("min_cibil")

    policy["lender"] = row["lender_name"]

    rate_band = policy.setdefault("rate_band", {})
    rate_band["effective_min"] = float(row["base_interest_rate_pct"]) / 100.0
    rate_band["_confidence"] = confidence

    min_cibil = policy.setdefault("min_cibil", {})
    if cibil_val is not None:
        min_cibil["value"] = int(cibil_val)
        min_cibil["_confidence"] = "verified" if confidence == "verified" else "soft"

    retirement = policy.setdefault("retirement_age", {})
    retirement["salaried"] = int(row["max_age_at_maturity"])
    retirement["self_employed"] = int(row["max_age_at_maturity"])

    tenure = policy.setdefault("max_tenure_years", {})
    tenure["value"] = int(row["max_tenure_years"])

    foir = policy.setdefault("foir_by_income_band", {})
    foir["band_low"] = float(row["foir_tier_1_pct"]) / 100.0
    foir["band_mid"] = float(row["foir_tier_2_pct"]) / 100.0
    foir["_confidence"] = confidence

    policy["ltv_slabs"] = {
        "upto_30L": float(row["ltv_up_to_30l_pct"]) / 100.0,
        "30L_to_75L": float(row["ltv_30l_to_75l_pct"]) / 100.0,
        "above_75L": float(row["ltv_above_75l_pct"]) / 100.0,
    }

    policy["_processing_fee_notes"] = row.get("processing_fee_notes", "")
    policy["_source"] = "supabase"
    return policy


def load_lender_policies(use_cloud: bool = True, fallback_folder: str = "lenders") -> list[dict]:
    """Fetches live policies from Supabase lending_rules; falls back to local JSONs on error."""
    local_policies = load_local_policies(fallback_folder)
    base_templates = {_lender_key(p["lender"]): p for p in local_policies}

    if use_cloud:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            try:
                from supabase import create_client
                client = create_client(url, key)
                response = client.table("lending_rules").select("*").order("lender_name").execute()
                if response.data:
                    return [_map_supabase_row_to_policy(row, base_templates) for row in response.data]
            except Exception as e:
                print(f"[WARN] Supabase fetch failed ({e}); falling back to local JSON policies.")

    return local_policies