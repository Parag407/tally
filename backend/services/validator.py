import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

def _parse_date(val: Any) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Try to parse a date.
    Returns: (parsed_date_str, original_val_str, is_standard_format)
    """
    if val is None:
        return None, None, False
        
    val_str = str(val).strip()
    if pd_is_na(val):
        return None, val_str, False

    if not val_str or str(val) == "nan":
        return None, val_str, False

    # Check if it's already standard DD-MM-YYYY
    if re.match(r"^\d{2}-\d{2}-\d{4}$", val_str):
        # Could be standard, just check valid date
        try:
            datetime.strptime(val_str, "%d-%m-%Y")
            return val_str, val_str, True
        except ValueError:
            pass

    formats = [
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", 
        "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%y", "%d/%m/%y",
        "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d",
        "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y",
        "%d.%m.%Y", "%d.%m.%y",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.strftime("%d-%m-%Y"), val_str, False
        except ValueError:
            continue

    try:
        from pandas import Timestamp
        if isinstance(val, Timestamp) or type(val).__name__ == 'Timestamp':
            return val.strftime("%d-%m-%Y"), val_str, False
    except Exception:
        pass

    return None, val_str, False

def pd_is_na(val):
    try:
        import pandas as pd
        return pd.isna(val)
    except:
        return str(val) == 'nan'

def _parse_number(val: Any) -> Tuple[Optional[float], Optional[str], bool]:
    """Returns (parsed_float, original_str, is_clean)"""
    if val is None or pd_is_na(val) or str(val) == "nan":
        return None, None, False
    
    val_str = str(val).strip()
    if not val_str:
        return None, val_str, False
        
    # Check if clean float
    try:
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val), val_str, True
            
        # Try pure float conversion
        clean_val = float(val_str)
        # If it was a string that successfully parsed as float without commas
        is_clean = not bool(re.search(r'[^\d.-]', val_str))
        return clean_val, val_str, is_clean
    except (ValueError, TypeError):
        # Try removing commas and currency symbols
        try:
            cleaned = re.sub(r'[^\d.-]', '', val_str)
            if cleaned:
                return float(cleaned), val_str, False
        except (ValueError, TypeError):
            pass
            
    return None, val_str, False

def create_error(row: int, field: str, current_value: str, error_msg: str, expected: str, suggested_fix: str, steps: List[str], can_auto_fix: bool) -> Dict:
    return {
        "row": row,
        "field": field,
        "current_value": current_value or "Empty/Blank",
        "error": error_msg,
        "expected_format": expected,
        "suggested_fix": suggested_fix,
        "solution_steps": steps,
        "can_auto_fix": can_auto_fix,
        "is_critical": not can_auto_fix
    }

# --------------- Bank Voucher Validation ---------------

def validate_bank(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    cleaned = []

    for rec in records:
        row = rec.get("_row", "?")
        row_errors = []
        clean = {"_row": row}

        # Date
        parsed_date, orig_date_str, is_date_standard = _parse_date(rec.get("date"))
        
        if not parsed_date:
            row_errors.append(create_error(
                row, "DATE", orig_date_str, "Invalid or missing date", "DD-MM-YYYY", None,
                ["Enter a valid date in DD-MM-YYYY format", "Example: 05-04-2025", "Ensure column is formatted as text or date in Excel"],
                False
            ))
        elif not is_date_standard:
            row_errors.append(create_error(
                row, "DATE", orig_date_str, "Non-standard date format or timestamp included", "DD-MM-YYYY", parsed_date,
                ["Convert date to DD-MM-YYYY format", "In Excel: Select column -> Format Cells -> Custom -> DD-MM-YYYY", "Or use formula: =TEXT(A2,\"DD-MM-YYYY\")"],
                True
            ))
        clean["date"] = parsed_date

        # Amount
        amount, orig_amt, amt_clean = _parse_number(rec.get("amount"))
        debit, orig_deb, deb_clean = _parse_number(rec.get("debit"))
        credit, orig_cred, cred_clean = _parse_number(rec.get("credit"))

        if amount is not None:
            if not amt_clean:
                row_errors.append(create_error(row, "AMOUNT", orig_amt, "Contains formatting characters (commas, spaces, or currency symbols)", "Numeric without commas", str(amount), ["Remove commas and spaces", "Select column -> Format Cells -> Number -> Remove thousand separator"], True))
            clean["amount"] = amount
        elif debit is not None:
            if not deb_clean:
                row_errors.append(create_error(row, "DEBIT AMOUNT", orig_deb, "Contains formatting characters", "Numeric without commas", str(debit), ["Remove commas"], True))
            clean["amount"] = debit
            clean["is_debit"] = True
        elif credit is not None:
            if not cred_clean:
                row_errors.append(create_error(row, "CREDIT AMOUNT", orig_cred, "Contains formatting characters", "Numeric without commas", str(credit), ["Remove commas"], True))
            clean["amount"] = credit
            clean["is_debit"] = False
        else:
            row_errors.append(create_error(
                row, "AMOUNT", "Empty", "Amount is required", "Numeric (e.g. 1500.50)", None,
                ["Provide a valid number for amount, debit, or credit"], False
            ))
            clean["amount"] = None

        vtype = str(rec.get("type", "") or "").strip().lower()
        if not vtype or vtype == "nan": vtype = ""
        
        if vtype in ("payment", "pay", "debit", "dr"):
            clean["voucher_type"] = "Payment"
        elif vtype in ("receipt", "recv", "credit", "cr"):
            clean["voucher_type"] = "Receipt"
        else:
            clean["voucher_type"] = "Payment"

        voucher_no = str(rec.get("voucher_no", "") or "").strip()
        if voucher_no == 'nan': voucher_no = ""
        clean["voucher_no"] = voucher_no or None
        
        debit_ledger = str(rec.get("debit", "") or "").strip()
        if debit_ledger == 'nan': debit_ledger = ""
        clean["debit_ledger"] = debit_ledger if type(rec.get("debit")) == str else None
        
        credit_ledger = str(rec.get("credit", "") or "").strip()
        if credit_ledger == 'nan': credit_ledger = ""
        clean["credit_ledger"] = credit_ledger if type(rec.get("credit")) == str else None
        
        narration = str(rec.get("narration", "") or "").strip()
        if narration == 'nan': narration = ""
        clean["narration"] = narration

        errors.extend(row_errors)
        clean["has_errors"] = any(e["is_critical"] for e in row_errors)
        cleaned.append(clean)

    return cleaned, errors


# --------------- Sales Voucher Validation ---------------

def validate_sales(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    cleaned = []

    for rec in records:
        row = rec.get("_row", "?")
        row_errors = []
        clean = {"_row": row}

        # Date
        parsed_date, orig_date_str, is_date_standard = _parse_date(rec.get("date"))
        if not parsed_date:
            row_errors.append(create_error(row, "DATE", orig_date_str, "Invalid date", "DD-MM-YYYY", None, ["Enter valid date"], False))
        clean["date"] = parsed_date

        # Party name
        party = str(rec.get("party_name", "") or "").strip()
        if not party or party == 'nan':
            row_errors.append(create_error(row, "CASH/PARTY", "Empty", "Party Name is missing", "Text", None, ["Enter customer name"], False))
        clean["party_name"] = party

        # Main Amount (Taxable Amount)
        taxable_amt, orig_taxable, taxable_clean = _parse_number(rec.get("amount"))
        if taxable_amt is None:
            row_errors.append(create_error(row, "TAXABLE AMOUNT", "Empty", "Taxable amount is required", "Numeric", None, ["Enter taxable amount"], False))
        clean["taxable_amount"] = taxable_amt

        # Bill Amount (Total)
        bill_amt, orig_bill, bill_clean = _parse_number(rec.get("bill_amount"))
        if bill_amt is None:
            # Fallback to taxable if bill is missing
            clean["bill_amount"] = taxable_amt
        else:
            clean["bill_amount"] = bill_amt

        # GST Ledgers
        clean["ledger_name"] = str(rec.get("ledger_name", "") or "").strip()
        clean["cgst_ledger"] = str(rec.get("cgst_ledger", "") or "").strip()
        clean["sgst_ledger"] = str(rec.get("sgst_ledger", "") or "").strip()
        
        tax_amt, _, _ = _parse_number(rec.get("tax_amount"))
        clean["tax_amount"] = tax_amt or 0.0
        
        clean["gst_slab"] = str(rec.get("gst_slab", "") or "").strip()
        clean["voucher_no"] = str(rec.get("voucher_no", "") or "").strip()
        clean["narration"] = str(rec.get("narration", "") or "").strip()
        clean["place_of_supply"] = str(rec.get("place_of_supply", "") or "").strip()

        errors.extend(row_errors)
        clean["has_errors"] = any(e["is_critical"] for e in row_errors)
        cleaned.append(clean)

    return cleaned, errors


# --------------- Purchase Voucher Validation ---------------

def validate_purchase(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    # Purchases share almost identical validation to sales in this new format
    errors = []
    cleaned = []

    for rec in records:
        row = rec.get("_row", "?")
        row_errors = []
        clean = {"_row": row}

        # Date
        parsed_date, orig_date_str, is_date_standard = _parse_date(rec.get("date"))
        if not parsed_date:
            row_errors.append(create_error(row, "DATE", orig_date_str, "Invalid date", "DD-MM-YYYY", None, ["Enter valid date"], False))
        clean["date"] = parsed_date

        # Party name
        party = str(rec.get("party_name", "") or "").strip()
        if not party or party == 'nan':
            row_errors.append(create_error(row, "CASH/PARTY", "Empty", "Party Name is missing", "Text", None, ["Enter supplier name"], False))
        clean["party_name"] = party

        # Main Amount (Taxable Amount)
        taxable_amt, orig_taxable, taxable_clean = _parse_number(rec.get("amount"))
        if taxable_amt is None:
            row_errors.append(create_error(row, "TAXABLE AMOUNT", "Empty", "Taxable amount is required", "Numeric", None, ["Enter taxable amount"], False))
        clean["taxable_amount"] = taxable_amt

        # Bill Amount (Total)
        bill_amt, orig_bill, bill_clean = _parse_number(rec.get("bill_amount"))
        if bill_amt is None:
            # Fallback to taxable if bill is missing
            clean["bill_amount"] = taxable_amt
        else:
            clean["bill_amount"] = bill_amt

        # GST Ledgers
        clean["ledger_name"] = str(rec.get("ledger_name", "") or "").strip()
        clean["cgst_ledger"] = str(rec.get("cgst_ledger", "") or "").strip()
        clean["sgst_ledger"] = str(rec.get("sgst_ledger", "") or "").strip()
        
        tax_amt, _, _ = _parse_number(rec.get("tax_amount"))
        clean["tax_amount"] = tax_amt or 0.0
        
        clean["gst_slab"] = str(rec.get("gst_slab", "") or "").strip()
        clean["voucher_no"] = str(rec.get("voucher_no", "") or "").strip()
        clean["narration"] = str(rec.get("narration", "") or "").strip()
        clean["place_of_supply"] = str(rec.get("place_of_supply", "") or "").strip()

        errors.extend(row_errors)
        clean["has_errors"] = any(e["is_critical"] for e in row_errors)
        cleaned.append(clean)

    return cleaned, errors


# --------------- Debit Note Validation ---------------

def _validate_note_common(records: List[Dict], voucher_label: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Shared validation logic for Debit Note and Credit Note vouchers.
    Both have identical field requirements; only the label differs.
    """
    errors = []
    cleaned = []
    seen_voucher_nos: Dict[str, List[int]] = {}

    for rec in records:
        row = rec.get("_row", "?")
        row_errors = []
        clean = {"_row": row}

        # ---- Date ----
        parsed_date, orig_date_str, is_date_standard = _parse_date(rec.get("date"))
        if not parsed_date:
            row_errors.append(create_error(
                row, "DATE", orig_date_str,
                "Invalid or missing date", "DD-MM-YYYY", None,
                ["Enter a valid date in DD-MM-YYYY format", "Example: 15-04-2025"],
                False
            ))
        elif not is_date_standard:
            row_errors.append(create_error(
                row, "DATE", orig_date_str,
                "Non-standard date format (timestamp or slashed format)",
                "DD-MM-YYYY", parsed_date,
                ["Convert to DD-MM-YYYY", "In Excel: Format Cells → Custom → DD-MM-YYYY"],
                True
            ))
        clean["date"] = parsed_date

        # ---- Party Name ----
        party = str(rec.get("party_name", "") or "").strip()
        if not party or party == "nan":
            row_errors.append(create_error(
                row, "PARTY NAME", "Empty",
                "Party Name is required for Note vouchers", "Text",
                None, ["Enter the party / customer / supplier name"], False
            ))
        clean["party_name"] = party

        # ---- Voucher No ----
        vch_no = str(rec.get("voucher_no", "") or "").strip()
        if vch_no == "nan": vch_no = ""
        if not vch_no:
            row_errors.append(create_error(
                row, "VOUCHER NO", "Empty",
                "Voucher number is required", "Alphanumeric",
                None, ["Enter a unique voucher/note number"], False
            ))
        clean["voucher_no"] = vch_no

        # Duplicate detection (non-critical warning)
        if vch_no:
            seen_voucher_nos.setdefault(vch_no, []).append(row)

        # ---- Taxable Amount ----
        taxable_amt, orig_taxable, taxable_clean = _parse_number(rec.get("taxable_amount"))
        if taxable_amt is None:
            row_errors.append(create_error(
                row, "TAXABLE AMOUNT", str(orig_taxable or "Empty"),
                "Taxable Amount is required and must be numeric",
                "Numeric (e.g. 50000.00)", None,
                ["Enter a valid numeric taxable amount", "Remove any currency symbols or commas"],
                False
            ))
        elif not taxable_clean:
            row_errors.append(create_error(
                row, "TAXABLE AMOUNT", str(orig_taxable),
                "Contains formatting characters (commas, spaces, or symbols)",
                "Numeric without commas", str(taxable_amt),
                ["Remove commas/currency symbols from the amount column"], True
            ))
        clean["taxable_amount"] = taxable_amt

        # ---- Total / Bill Amount ----
        bill_amt, _, _ = _parse_number(rec.get("bill_amount") or rec.get("total_amount"))
        clean["bill_amount"] = bill_amt if bill_amt is not None else taxable_amt

        # ---- GST Percentages (numeric check) ----
        for gst_field, label in [("cgst_pct", "CGST %"), ("sgst_pct", "SGST %"), ("igst_pct", "IGST %")]:
            val_raw = rec.get(gst_field)
            if val_raw is not None and str(val_raw).strip() not in ("", "nan", "0", "0.0"):
                gst_num, _, gst_clean = _parse_number(val_raw)
                if gst_num is None:
                    row_errors.append(create_error(
                        row, label, str(val_raw),
                        f"{label} must be a numeric percentage",
                        "Numeric (e.g. 9 for 9%)", None,
                        [f"Enter {label} as a plain number like 9 or 18"], False
                    ))
                clean[gst_field] = gst_num or 0.0
            else:
                clean[gst_field] = 0.0

        # ---- Tax Amount (optional, derived if missing) ----
        tax_amt, _, _ = _parse_number(rec.get("tax_amount"))
        clean["tax_amount"] = tax_amt or 0.0

        # ---- GST Ledger Names ----
        clean["ledger_name"] = str(rec.get("ledger_name", "") or "").strip()
        clean["cgst_ledger"] = str(rec.get("cgst_ledger", "") or "").strip()
        clean["sgst_ledger"] = str(rec.get("sgst_ledger", "") or "").strip()
        clean["igst_ledger"] = str(rec.get("igst_ledger", "") or "").strip()

        # ---- Reason / Narration ----
        clean["reason"] = str(rec.get("reason", "") or rec.get("narration", "") or "").strip()
        clean["narration"] = clean["reason"]

        errors.extend(row_errors)
        clean["has_errors"] = any(e["is_critical"] for e in row_errors)
        cleaned.append(clean)

    # ---- Post-pass: duplicate voucher number warnings ----
    for vch_no, rows in seen_voucher_nos.items():
        if len(rows) > 1:
            for dup_row in rows:
                errors.append({
                    "row": dup_row,
                    "field": "VOUCHER NO",
                    "current_value": vch_no,
                    "error": f"Duplicate voucher number '{vch_no}' found in rows: {rows}",
                    "expected_format": "Unique per voucher",
                    "suggested_fix": None,
                    "solution_steps": ["Ensure each note has a unique voucher number"],
                    "can_auto_fix": False,
                    "is_critical": False,
                })

    return cleaned, errors


def validate_debit_note(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Validate records for Debit Note vouchers."""
    return _validate_note_common(records, "Debit Note")


def validate_credit_note(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Validate records for Credit Note vouchers."""
    return _validate_note_common(records, "Credit Note")
