"""
Smart Column Mapper
Rule-based + optional AI-powered column name mapping.
Handles typos, abbreviations, and alternate column names.
"""
import os
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional

# ---------- canonical column aliases per voucher type ----------

BANK_ALIASES: Dict[str, List[str]] = {
    "date": ["date", "dt", "txn date", "transaction date", "trans date", "value date", "posting date"],
    "voucher_no": ["voucher no", "voucher no (optional)", "voucher_no", "vch no", "vch_no", "ref no", "reference", "ref", "voucher number"],
    "debit": ["by - dr", "by-dr", "by dr", "debit", "dr", "debit amount", "dr amount", "dr amt"],
    "credit": ["to - cr", "to-cr", "to cr", "credit", "cr", "credit amount", "cr amount", "cr amt"],
    "amount": ["amount", "amt", "value", "total", "net amount", "net amt", "txn amount"],
    "narration": ["narration", "description", "desc", "remarks", "particulars", "details", "memo", "note"],
    "type": ["type", "voucher type", "vch type", "txn type", "transaction type", "mode"],
}

SALES_ALIASES: Dict[str, List[str]] = {
    "date": ["date", "dt", "invoice date", "inv date", "bill date", "sale date"],
    "voucher_no": ["voucher no", "invoice no", "inv no", "bill no", "ref no", "reference"],
    "party_name": ["cash/party", "party name", "party", "customer", "buyer", "sold to", "bill to"],
    "ledger_name": ["purchase/sales ledger", "sales ledger", "sales account", "income ledger"],
    "cgst_ledger": ["igst/central gst ledger", "cgst ledger", "igst ledger", "central tax"],
    "sgst_ledger": ["ut/state gst ledger", "sgst ledger", "state tax", "utgst ledger"],
    "amount": ["taxable amount", "taxable value", "assessable value"],
    "tax_amount": ["gst", "tax amount", "total tax"],
    "bill_amount": ["bill amount", "total amount", "net amount", "invoice value"],
    "gst_slab": ["gst slab", "tax slab", "gst %", "tax %"],
    "place_of_supply": ["place of supply", "state", "pos"],
    "narration": ["narration", "description", "remarks", "memo", "note"],
    "type": ["type", "voucher type"],
}

PURCHASE_ALIASES: Dict[str, List[str]] = {
    "date": ["date", "dt", "invoice date", "inv date", "bill date", "purchase date"],
    "voucher_no": ["voucher no", "invoice no", "inv no", "bill no", "ref no", "reference"],
    "party_name": ["cash/party", "party name", "party", "supplier", "vendor", "purchased from"],
    "ledger_name": ["purchase/sales ledger", "purchase ledger", "purchase account", "expense ledger"],
    "cgst_ledger": ["igst/central gst ledger", "cgst ledger", "igst ledger", "central tax"],
    "sgst_ledger": ["ut/state gst ledger", "sgst ledger", "state tax", "utgst ledger"],
    "amount": ["taxable amount", "taxable value", "assessable value"],
    "tax_amount": ["gst", "tax amount", "total tax"],
    "bill_amount": ["bill amount", "total amount", "net amount", "invoice value"],
    "gst_slab": ["gst slab", "tax slab", "gst %", "tax %"],
    "place_of_supply": ["place of supply", "state", "pos"],
    "narration": ["narration", "description", "remarks", "memo", "note"],
    "type": ["type", "voucher type"],
}

ALIAS_MAP = {
    "bank": BANK_ALIASES,
    "sales": SALES_ALIASES,
    "purchase": PURCHASE_ALIASES,
}

# Debit Note and Credit Note share the same column schema
NOTE_ALIASES: Dict[str, List[str]] = {
    "date": ["date", "dt", "note date", "invoice date", "bill date"],
    "voucher_no": ["voucher no", "note no", "debit note no", "credit note no", "inv no", "ref no", "reference"],
    "party_name": ["party name", "cash/party", "party", "customer", "supplier", "buyer", "vendor", "bill to", "sold to"],
    "ledger_name": [
        "ledger", "return ledger", "purchase/sales ledger", "sales return ledger",
        "purchase return ledger", "income ledger", "expense ledger",
    ],
    "cgst_ledger": ["igst/central gst ledger", "cgst ledger", "central gst ledger", "central tax", "cgst a/c"],
    "sgst_ledger": ["ut/state gst ledger", "sgst ledger", "state gst ledger", "state tax", "sgst a/c"],
    "igst_ledger": ["igst ledger", "integrated gst ledger", "igst a/c"],
    "taxable_amount": ["taxable amount", "taxable value", "assessable value", "net amount"],
    "cgst_pct": ["cgst %", "cgst rate", "cgst percent", "central gst %"],
    "sgst_pct": ["sgst %", "sgst rate", "sgst percent", "state gst %"],
    "igst_pct": ["igst %", "igst rate", "igst percent", "integrated gst %"],
    "tax_amount": ["tax amount", "gst", "total tax", "tax total"],
    "bill_amount": ["bill amount", "total amount", "total", "invoice value", "net payable"],
    "reason": ["reason", "narration", "description", "remarks", "memo", "details", "note"],
}

ALIAS_MAP["debit_note"] = NOTE_ALIASES
ALIAS_MAP["credit_note"] = NOTE_ALIASES


def _normalize(name: str) -> str:
    """Lowercase, strip, collapse whitespace, remove special chars."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def rule_based_map(columns: List[str], voucher_type: str) -> Dict[str, Optional[str]]:
    """
    Map incoming Excel column names to canonical names using aliases.
    Returns {canonical_name: matched_excel_column | None}
    """
    aliases = ALIAS_MAP.get(voucher_type, BANK_ALIASES)
    mapping: Dict[str, Optional[str]] = {}
    used_columns = set()

    for canonical, alias_list in aliases.items():
        best_match = None
        best_score = 0.0

        for col in columns:
            if col in used_columns:
                continue
            norm_col = _normalize(col)

            # Exact match
            if norm_col in [_normalize(a) for a in alias_list]:
                best_match = col
                best_score = 1.0
                break

            # Fuzzy match
            for alias in alias_list:
                score = _similarity(norm_col, _normalize(alias))
                if score > best_score and score >= 0.65:
                    best_score = score
                    best_match = col

        mapping[canonical] = best_match
        if best_match:
            used_columns.add(best_match)

    return mapping


async def ai_based_map(columns: List[str], voucher_type: str) -> Dict[str, Optional[str]]:
    """
    Use OpenAI to intelligently map column names when rule-based fails.
    Falls back to rule-based if API key is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-openai-api-key-here":
        return rule_based_map(columns, voucher_type)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)
        aliases = ALIAS_MAP.get(voucher_type, BANK_ALIASES)
        canonical_names = list(aliases.keys())

        prompt = f"""You are a data mapping expert. Map these Excel column names to canonical column names.

Excel columns: {columns}
Canonical columns: {canonical_names}
Voucher type: {voucher_type}

Return ONLY a JSON object where keys are canonical names and values are the matching Excel column name or null if no match.
Example: {{"date": "Trans Date", "amount": "Amt", "narration": null}}
Return raw JSON only, no markdown."""

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
        )

        import json
        result = json.loads(response.choices[0].message.content.strip())
        # Validate that mapped values actually exist in columns
        validated = {}
        for k, v in result.items():
            if k in canonical_names:
                validated[k] = v if v in columns else None
        return validated

    except Exception:
        return rule_based_map(columns, voucher_type)


def get_mapping(columns: List[str], voucher_type: str, use_ai: bool = False):
    """
    Primary entry point. Returns column mapping dict.
    """
    if use_ai:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're inside an async context already - caller should await ai_based_map directly
            return rule_based_map(columns, voucher_type)
        return loop.run_until_complete(ai_based_map(columns, voucher_type))
    return rule_based_map(columns, voucher_type)
