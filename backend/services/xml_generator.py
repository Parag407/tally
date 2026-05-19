import logging
import re
from datetime import datetime
from typing import Dict, List, Any
from xml.sax.saxutils import escape as xml_escape
from lxml import etree

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _sanitize_text(text: Any, default: str = "Not Provided") -> str:
    """Trim spaces, remove special characters, prevent null. For NON-ledger fields only."""
    if text is None:
        return default
    val_str = str(text).strip()
    if not val_str:
        return default
    val_str = re.sub(r'[^\w\s\-\.,\/\(\)\[\]#]', '', val_str)
    val_str = val_str.strip()
    return val_str if val_str else default

def _safe_ledger_name(text: Any, default: str = "", field_name: str = "ledger") -> str:
    """
    Preserve ALL special characters exactly as entered.
    Only strips leading/trailing whitespace.
    Logs debug info for integrity checks.
    """
    original = text
    if text is None:
        logger.debug(f"Ledger [{field_name}]: None -> default '{default}'")
        return default
    val_str = str(text).strip()
    if not val_str:
        logger.debug(f"Ledger [{field_name}]: empty after strip -> default '{default}'")
        return val_str if val_str else default
    if str(original) != val_str and str(original).strip() == val_str:
        logger.debug(f"Ledger [{field_name}]: trimmed whitespace only")
    logger.debug(f"Ledger [{field_name}]: original='{original}' -> '{val_str}'")
    return val_str

def validate_ledger_integrity(records: List[Dict], ledger_fields: List[str]) -> List[str]:
    """
    Compare original ledger names from Excel with processed values.
    Returns list of error messages for any mismatches.
    """
    errors = []
    for rec in records:
        row = rec.get("_row", "?")
        for field in ledger_fields:
            original = rec.get(f"_{field}_original")
            processed = rec.get(field)
            if original and processed:
                if str(original).strip() != str(processed).strip():
                    msg = (f"Row {row}: Ledger name modified during processing: "
                           f"'{original}' -> '{processed}'")
                    logger.error(msg)
                    errors.append(msg)
    return errors


def verify_ledger_names_in_xml(xml_content: str, records: List[Dict], ledger_fields: List[str]) -> List[str]:
    """
    Verify that every original ledger name appears unchanged in the generated XML.
    Compares Excel ledger names with <LEDGERNAME> values in the final XML output.
    Handles XML escaping (e.g. & becomes &amp;).
    """
    errors = []
    seen_names = set()
    for rec in records:
        row = rec.get("_row", "?")
        for field in ledger_fields:
            original = rec.get(field)
            if original and str(original).strip():
                orig_str = str(original).strip()
                escaped = xml_escape(orig_str)
                tag = f"<LEDGERNAME>{escaped}</LEDGERNAME>"
                if tag not in xml_content and orig_str not in seen_names:
                    msg = (f"Row {row} - {field}: Ledger name modified during processing: "
                           f"original '{orig_str}' not found in generated XML as <LEDGERNAME>")
                    logger.error(msg)
                    errors.append(msg)
                    seen_names.add(orig_str)
                elif orig_str not in seen_names:
                    logger.debug(f"Row {row} - {field}: XML ledger verified successfully as <LEDGERNAME>{escaped}</LEDGERNAME>")
                    seen_names.add(orig_str)
    return errors


# Ledger fields per voucher type for validation
LEDGER_FIELDS_BANK = ["debit_ledger", "credit_ledger"]
LEDGER_FIELDS_SALES = ["party_name", "ledger_name", "cgst_ledger", "sgst_ledger"]
LEDGER_FIELDS_PURCHASE = ["party_name", "ledger_name", "cgst_ledger", "sgst_ledger"]
LEDGER_FIELDS_DEBIT_NOTE = ["party_name", "ledger_name", "cgst_ledger", "sgst_ledger", "igst_ledger"]
LEDGER_FIELDS_CREDIT_NOTE = ["party_name", "ledger_name", "cgst_ledger", "sgst_ledger", "igst_ledger"]

def _clean_number(val: Any) -> float:
    """Ensure clean numeric values, remove commas, symbols etc."""
    if val is None:
        return 0.0
    val_str = str(val).replace('₹', '').replace(',', '').strip()
    try:
        return round(float(val_str), 2)
    except ValueError:
        return 0.0

def _tally_date(date_str: str) -> str:
    """Convert DD-MM-YYYY to YYYYMMDD (Tally format)."""
    if not date_str:
        return datetime.now().strftime("%Y%m%d")
    try:
        dt = datetime.strptime(str(date_str).strip(), "%d-%m-%Y")
        return dt.strftime("%Y%m%d")
    except (ValueError, TypeError):
        try:
            # Fallback for YYYY-MM-DD
            dt = datetime.strptime(str(date_str).strip()[:10], "%Y-%m-%d")
            return dt.strftime("%Y%m%d")
        except (ValueError, TypeError):
            return datetime.now().strftime("%Y%m%d")

def _add_element(parent, tag, text) -> None:
    """Helper to prevent empty/null tags."""
    if text is not None and str(text).strip() != "":
        etree.SubElement(parent, tag).text = str(text).strip()


def generate_bank_xml(records: List[Dict], bank_name: str = "Bank Account") -> str:
    """
    Generate Tally XML for bank payment/receipt vouchers.
    """
    envelope = etree.Element("ENVELOPE")
    header = etree.SubElement(envelope, "HEADER")
    etree.SubElement(header, "TALLYREQUEST").text = "Import Data"

    body = etree.SubElement(envelope, "BODY")
    import_data = etree.SubElement(body, "IMPORTDATA")

    request_desc = etree.SubElement(import_data, "REQUESTDESC")
    etree.SubElement(request_desc, "REPORTNAME").text = "Vouchers"
    static_vars = etree.SubElement(request_desc, "STATICVARIABLES")
    etree.SubElement(static_vars, "SVCURRENTCOMPANY").text = "##SVCURRENTCOMPANY"

    request_data = etree.SubElement(import_data, "REQUESTDATA")

    for rec in records:
        if rec.get("has_errors"):
            continue

        voucher_type = _sanitize_text(rec.get("voucher_type"), "Payment")
        tally_date = _tally_date(rec.get("date", ""))
        amount = _clean_number(rec.get("amount", 0))
        
        if amount == 0:
            continue

        tallymsg = etree.SubElement(request_data, "TALLYMESSAGE", xmlns_UDF="TallyUDF")
        voucher = etree.SubElement(tallymsg, "VOUCHER", VCHTYPE=voucher_type, ACTION="Create")

        _add_element(voucher, "DATE", tally_date)
        _add_element(voucher, "VOUCHERTYPENAME", voucher_type)

        vch_no = rec.get("voucher_no")
        if vch_no and str(vch_no).strip():
            _add_element(voucher, "VOUCHERNUMBER", _sanitize_text(vch_no, ""))

        narration = _sanitize_text(rec.get("narration"), "Bank Transaction")
        _add_element(voucher, "NARRATION", narration)

        balanced_amount = abs(amount)

        # Map Debit ledger directly from Excel row (preserve all special chars)
        debit_ledger = _safe_ledger_name(rec.get("debit_ledger"), "Missing Debit Ledger", "debit_ledger")
        alloc_debit = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(alloc_debit, "LEDGERNAME", debit_ledger)
        _add_element(alloc_debit, "ISDEEMEDPOSITIVE", "Yes")
        _add_element(alloc_debit, "AMOUNT", f"-{balanced_amount:.2f}")

        # Map Credit ledger directly from Excel row (preserve all special chars)
        credit_ledger = _safe_ledger_name(rec.get("credit_ledger"), "Missing Credit Ledger", "credit_ledger")
        alloc_credit = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(alloc_credit, "LEDGERNAME", credit_ledger)
        _add_element(alloc_credit, "ISDEEMEDPOSITIVE", "No")
        _add_element(alloc_credit, "AMOUNT", f"{balanced_amount:.2f}")

    tree = etree.ElementTree(envelope)
    return etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")


def generate_sales_xml(records: List[Dict], sales_ledger: str = "Sales Account") -> str:
    """
    Generate Tally XML for Sales using the new explicit ledger format.
    """
    envelope = etree.Element("ENVELOPE")
    header = etree.SubElement(envelope, "HEADER")
    etree.SubElement(header, "TALLYREQUEST").text = "Import Data"
    body = etree.SubElement(envelope, "BODY")
    import_data = etree.SubElement(body, "IMPORTDATA")
    request_desc = etree.SubElement(import_data, "REQUESTDESC")
    etree.SubElement(request_desc, "REPORTNAME").text = "Vouchers"
    static_vars = etree.SubElement(request_desc, "STATICVARIABLES")
    etree.SubElement(static_vars, "SVCURRENTCOMPANY").text = "##SVCURRENTCOMPANY"
    request_data = etree.SubElement(import_data, "REQUESTDATA")

    for rec in records:
        if rec.get("has_errors"): continue
        
        taxable = _clean_number(rec.get("taxable_amount"))
        total = _clean_number(rec.get("bill_amount"))
        tax = _clean_number(rec.get("tax_amount"))
        
        tallymsg = etree.SubElement(request_data, "TALLYMESSAGE", xmlns_UDF="TallyUDF")
        voucher = etree.SubElement(tallymsg, "VOUCHER", VCHTYPE="Sales", ACTION="Create")
        
        _add_element(voucher, "DATE", _tally_date(rec.get("date")))
        _add_element(voucher, "VOUCHERTYPENAME", "Sales")
        _add_element(voucher, "PARTYNAME", _safe_ledger_name(rec.get("party_name"), "", "party_name"))
        _add_element(voucher, "VOUCHERNUMBER", _sanitize_text(rec.get("voucher_no"), ""))
        _add_element(voucher, "NARRATION", _sanitize_text(rec.get("narration"), "Sales Entry"))
        
        # Party (Debit) - preserve all special chars
        p_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(p_entry, "LEDGERNAME", _safe_ledger_name(rec.get("party_name"), "", "party_name"))
        _add_element(p_entry, "ISDEEMEDPOSITIVE", "Yes")
        _add_element(p_entry, "AMOUNT", f"-{total:.2f}")

        # Sales Ledger (Credit) - preserve all special chars
        s_ledger = _safe_ledger_name(rec.get("ledger_name"), "Sales Account", "ledger_name")
        s_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(s_entry, "LEDGERNAME", s_ledger)
        _add_element(s_entry, "ISDEEMEDPOSITIVE", "No")
        _add_element(s_entry, "AMOUNT", f"{taxable:.2f}")

        # GST Ledgers (Credit) - preserve all special chars
        cgst_ledger = _safe_ledger_name(rec.get("cgst_ledger"), "", "cgst_ledger")
        sgst_ledger = _safe_ledger_name(rec.get("sgst_ledger"), "", "sgst_ledger")
        
        if tax > 0:
            if cgst_ledger and sgst_ledger:
                # Split tax
                c_tax = round(tax / 2, 2)
                s_tax = round(tax - c_tax, 2)
                
                c_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(c_entry, "LEDGERNAME", cgst_ledger)
                _add_element(c_entry, "ISDEEMEDPOSITIVE", "No")
                _add_element(c_entry, "AMOUNT", f"{c_tax:.2f}")

                s_entry_tax = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(s_entry_tax, "LEDGERNAME", sgst_ledger)
                _add_element(s_entry_tax, "ISDEEMEDPOSITIVE", "No")
                _add_element(s_entry_tax, "AMOUNT", f"{s_tax:.2f}")
            elif cgst_ledger:
                # IGST Case probably
                i_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(i_entry, "LEDGERNAME", cgst_ledger)
                _add_element(i_entry, "ISDEEMEDPOSITIVE", "No")
                _add_element(i_entry, "AMOUNT", f"{tax:.2f}")

    tree = etree.ElementTree(envelope)
    return etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")


def generate_purchase_xml(records: List[Dict], purchase_ledger: str = "Purchase Account") -> str:
    """
    Generate Tally XML for Purchase using the new explicit ledger format.
    """
    envelope = etree.Element("ENVELOPE")
    header = etree.SubElement(envelope, "HEADER")
    etree.SubElement(header, "TALLYREQUEST").text = "Import Data"
    body = etree.SubElement(envelope, "BODY")
    import_data = etree.SubElement(body, "IMPORTDATA")
    request_desc = etree.SubElement(import_data, "REQUESTDESC")
    etree.SubElement(request_desc, "REPORTNAME").text = "Vouchers"
    static_vars = etree.SubElement(request_desc, "STATICVARIABLES")
    etree.SubElement(static_vars, "SVCURRENTCOMPANY").text = "##SVCURRENTCOMPANY"
    request_data = etree.SubElement(import_data, "REQUESTDATA")

    for rec in records:
        if rec.get("has_errors"): continue
        
        taxable = _clean_number(rec.get("taxable_amount"))
        total = _clean_number(rec.get("bill_amount"))
        tax = _clean_number(rec.get("tax_amount"))
        
        tallymsg = etree.SubElement(request_data, "TALLYMESSAGE", xmlns_UDF="TallyUDF")
        voucher = etree.SubElement(tallymsg, "VOUCHER", VCHTYPE="Purchase", ACTION="Create")
        
        _add_element(voucher, "DATE", _tally_date(rec.get("date")))
        _add_element(voucher, "VOUCHERTYPENAME", "Purchase")
        _add_element(voucher, "PARTYNAME", _safe_ledger_name(rec.get("party_name"), "", "party_name"))
        _add_element(voucher, "VOUCHERNUMBER", _sanitize_text(rec.get("voucher_no"), ""))
        _add_element(voucher, "NARRATION", _sanitize_text(rec.get("narration"), "Purchase Entry"))
        
        # Party (Credit) - preserve all special chars
        p_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(p_entry, "LEDGERNAME", _safe_ledger_name(rec.get("party_name"), "", "party_name"))
        _add_element(p_entry, "ISDEEMEDPOSITIVE", "No")
        _add_element(p_entry, "AMOUNT", f"{total:.2f}")

        # Purchase Ledger (Debit) - preserve all special chars
        p_ledger = _safe_ledger_name(rec.get("ledger_name"), "Purchase Account", "ledger_name")
        s_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(s_entry, "LEDGERNAME", p_ledger)
        _add_element(s_entry, "ISDEEMEDPOSITIVE", "Yes")
        _add_element(s_entry, "AMOUNT", f"-{taxable:.2f}")

        # GST Ledgers (Debit) - preserve all special chars
        cgst_ledger = _safe_ledger_name(rec.get("cgst_ledger"), "", "cgst_ledger")
        sgst_ledger = _safe_ledger_name(rec.get("sgst_ledger"), "", "sgst_ledger")
        
        if tax > 0:
            if cgst_ledger and sgst_ledger:
                # Split tax
                c_tax = round(tax / 2, 2)
                s_tax = round(tax - c_tax, 2)
                
                c_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(c_entry, "LEDGERNAME", cgst_ledger)
                _add_element(c_entry, "ISDEEMEDPOSITIVE", "Yes")
                _add_element(c_entry, "AMOUNT", f"-{c_tax:.2f}")

                s_entry_tax = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(s_entry_tax, "LEDGERNAME", sgst_ledger)
                _add_element(s_entry_tax, "ISDEEMEDPOSITIVE", "Yes")
                _add_element(s_entry_tax, "AMOUNT", f"-{s_tax:.2f}")
            elif cgst_ledger:
                # IGST Case
                i_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(i_entry, "LEDGERNAME", cgst_ledger)
                _add_element(i_entry, "ISDEEMEDPOSITIVE", "Yes")
                _add_element(i_entry, "AMOUNT", f"-{tax:.2f}")

    tree = etree.ElementTree(envelope)
    return etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")


def generate_debit_note_xml(records: List[Dict]) -> str:
    """
    Generate Tally Prime compatible XML for Debit Note vouchers.

    Accounting logic:
      - Party Ledger  → Credit  (ISDEEMEDPOSITIVE = No,  amount positive)
      - Purchase/Return Ledger → Debit (ISDEEMEDPOSITIVE = Yes, amount negative)
      - GST Ledgers   → Debit   (ISDEEMEDPOSITIVE = Yes, amount negative)
    """
    envelope = etree.Element("ENVELOPE")
    header = etree.SubElement(envelope, "HEADER")
    etree.SubElement(header, "TALLYREQUEST").text = "Import Data"
    body = etree.SubElement(envelope, "BODY")
    import_data = etree.SubElement(body, "IMPORTDATA")
    request_desc = etree.SubElement(import_data, "REQUESTDESC")
    etree.SubElement(request_desc, "REPORTNAME").text = "Vouchers"
    static_vars = etree.SubElement(request_desc, "STATICVARIABLES")
    etree.SubElement(static_vars, "SVCURRENTCOMPANY").text = "##SVCURRENTCOMPANY"
    request_data = etree.SubElement(import_data, "REQUESTDATA")

    seen_vouchers: set = set()

    for rec in records:
        if rec.get("has_errors"):
            continue

        taxable = _clean_number(rec.get("taxable_amount"))
        total = _clean_number(rec.get("bill_amount"))
        cgst_pct = _clean_number(rec.get("cgst_pct"))
        sgst_pct = _clean_number(rec.get("sgst_pct"))
        igst_pct = _clean_number(rec.get("igst_pct"))

        # Compute GST amounts from percentages when tax_amount is absent
        tax_from_rec = _clean_number(rec.get("tax_amount"))
        if tax_from_rec > 0:
            tax = tax_from_rec
        else:
            cgst_amt = round(taxable * cgst_pct / 100, 2)
            sgst_amt = round(taxable * sgst_pct / 100, 2)
            igst_amt = round(taxable * igst_pct / 100, 2)
            tax = cgst_amt + sgst_amt + igst_amt
            if total == 0:
                total = taxable + tax

        vch_no = _sanitize_text(rec.get("voucher_no"), "")
        if vch_no in seen_vouchers and vch_no:
            # Duplicate – still import but add suffix flag (Tally will handle)
            pass
        if vch_no:
            seen_vouchers.add(vch_no)

        reason = _sanitize_text(rec.get("reason"), "Purchase Return / Debit Note")

        tallymsg = etree.SubElement(request_data, "TALLYMESSAGE", xmlns_UDF="TallyUDF")
        voucher = etree.SubElement(tallymsg, "VOUCHER", VCHTYPE="Debit Note", ACTION="Create")

        _add_element(voucher, "DATE", _tally_date(rec.get("date")))
        _add_element(voucher, "VOUCHERTYPENAME", "Debit Note")
        _add_element(voucher, "PARTYNAME", _safe_ledger_name(rec.get("party_name"), "", "party_name"))
        _add_element(voucher, "VOUCHERNUMBER", vch_no)
        _add_element(voucher, "NARRATION", reason)
        _add_element(voucher, "ISINVOICE", "No")

        # Party → Credit (money going back to supplier) - preserve all special chars
        p_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(p_entry, "LEDGERNAME", _safe_ledger_name(rec.get("party_name"), "", "party_name"))
        _add_element(p_entry, "ISDEEMEDPOSITIVE", "No")
        _add_element(p_entry, "AMOUNT", f"{total:.2f}")

        # Return / Purchase ledger → Debit - preserve all special chars
        ret_ledger = _safe_ledger_name(rec.get("ledger_name"), "Purchase Return Account", "ledger_name")
        r_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(r_entry, "LEDGERNAME", ret_ledger)
        _add_element(r_entry, "ISDEEMEDPOSITIVE", "Yes")
        _add_element(r_entry, "AMOUNT", f"-{taxable:.2f}")

        # GST ledgers → Debit - preserve all special chars
        cgst_ledger = _safe_ledger_name(rec.get("cgst_ledger"), "", "cgst_ledger")
        sgst_ledger = _safe_ledger_name(rec.get("sgst_ledger"), "", "sgst_ledger")
        igst_ledger = _safe_ledger_name(rec.get("igst_ledger"), "", "igst_ledger")

        if tax > 0:
            if igst_pct > 0 and igst_ledger:
                i_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(i_entry, "LEDGERNAME", igst_ledger)
                _add_element(i_entry, "ISDEEMEDPOSITIVE", "Yes")
                _add_element(i_entry, "AMOUNT", f"-{tax:.2f}")
            elif cgst_ledger and sgst_ledger:
                c_tax = round(tax / 2, 2)
                s_tax = round(tax - c_tax, 2)
                c_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(c_entry, "LEDGERNAME", cgst_ledger)
                _add_element(c_entry, "ISDEEMEDPOSITIVE", "Yes")
                _add_element(c_entry, "AMOUNT", f"-{c_tax:.2f}")
                s_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(s_entry, "LEDGERNAME", sgst_ledger)
                _add_element(s_entry, "ISDEEMEDPOSITIVE", "Yes")
                _add_element(s_entry, "AMOUNT", f"-{s_tax:.2f}")

    tree = etree.ElementTree(envelope)
    return etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")


def generate_credit_note_xml(records: List[Dict]) -> str:
    """
    Generate Tally Prime compatible XML for Credit Note vouchers.

    Accounting logic:
      - Party Ledger  → Debit   (ISDEEMEDPOSITIVE = Yes, amount negative)
      - Sales/Return Ledger → Credit (ISDEEMEDPOSITIVE = No, amount positive)
      - GST Ledgers   → Credit  (ISDEEMEDPOSITIVE = No, amount positive)
    """
    envelope = etree.Element("ENVELOPE")
    header = etree.SubElement(envelope, "HEADER")
    etree.SubElement(header, "TALLYREQUEST").text = "Import Data"
    body = etree.SubElement(envelope, "BODY")
    import_data = etree.SubElement(body, "IMPORTDATA")
    request_desc = etree.SubElement(import_data, "REQUESTDESC")
    etree.SubElement(request_desc, "REPORTNAME").text = "Vouchers"
    static_vars = etree.SubElement(request_desc, "STATICVARIABLES")
    etree.SubElement(static_vars, "SVCURRENTCOMPANY").text = "##SVCURRENTCOMPANY"
    request_data = etree.SubElement(import_data, "REQUESTDATA")

    seen_vouchers: set = set()

    for rec in records:
        if rec.get("has_errors"):
            continue

        taxable = _clean_number(rec.get("taxable_amount"))
        total = _clean_number(rec.get("bill_amount"))
        cgst_pct = _clean_number(rec.get("cgst_pct"))
        sgst_pct = _clean_number(rec.get("sgst_pct"))
        igst_pct = _clean_number(rec.get("igst_pct"))

        tax_from_rec = _clean_number(rec.get("tax_amount"))
        if tax_from_rec > 0:
            tax = tax_from_rec
        else:
            cgst_amt = round(taxable * cgst_pct / 100, 2)
            sgst_amt = round(taxable * sgst_pct / 100, 2)
            igst_amt = round(taxable * igst_pct / 100, 2)
            tax = cgst_amt + sgst_amt + igst_amt
            if total == 0:
                total = taxable + tax

        vch_no = _sanitize_text(rec.get("voucher_no"), "")
        if vch_no in seen_vouchers and vch_no:
            pass
        if vch_no:
            seen_vouchers.add(vch_no)

        reason = _sanitize_text(rec.get("reason"), "Sales Return / Credit Note")

        tallymsg = etree.SubElement(request_data, "TALLYMESSAGE", xmlns_UDF="TallyUDF")
        voucher = etree.SubElement(tallymsg, "VOUCHER", VCHTYPE="Credit Note", ACTION="Create")

        party_name_safe = _safe_ledger_name(rec.get("party_name"), "", "party_name")

        _add_element(voucher, "DATE", _tally_date(rec.get("date")))
        _add_element(voucher, "VOUCHERTYPENAME", "Credit Note")
        _add_element(voucher, "PARTYNAME", party_name_safe)
        _add_element(voucher, "VOUCHERNUMBER", vch_no)
        _add_element(voucher, "NARRATION", reason)
        _add_element(voucher, "ISINVOICE", "No")

        # Party → Debit (customer owes less now) - preserve all special chars
        p_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(p_entry, "LEDGERNAME", party_name_safe)
        _add_element(p_entry, "ISDEEMEDPOSITIVE", "Yes")
        _add_element(p_entry, "AMOUNT", f"-{total:.2f}")

        # Sales Return ledger → Credit - preserve all special chars
        ret_ledger = _safe_ledger_name(rec.get("ledger_name"), "Sales Return Account", "ledger_name")
        
        r_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
        _add_element(r_entry, "LEDGERNAME", ret_ledger)
        _add_element(r_entry, "ISDEEMEDPOSITIVE", "No")
        _add_element(r_entry, "AMOUNT", f"{taxable:.2f}")

        # GST ledgers → Credit (reversing the tax collected) - preserve all special chars
        cgst_ledger = _safe_ledger_name(rec.get("cgst_ledger"), "", "cgst_ledger")
        sgst_ledger = _safe_ledger_name(rec.get("sgst_ledger"), "", "sgst_ledger")
        igst_ledger = _safe_ledger_name(rec.get("igst_ledger"), "", "igst_ledger")


        if tax > 0:
            if igst_pct > 0 and igst_ledger:
                i_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(i_entry, "LEDGERNAME", igst_ledger)
                _add_element(i_entry, "ISDEEMEDPOSITIVE", "No")
                _add_element(i_entry, "AMOUNT", f"{tax:.2f}")
            elif cgst_ledger and sgst_ledger:
                c_tax = round(tax / 2, 2)
                s_tax = round(tax - c_tax, 2)
                c_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(c_entry, "LEDGERNAME", cgst_ledger)
                _add_element(c_entry, "ISDEEMEDPOSITIVE", "No")
                _add_element(c_entry, "AMOUNT", f"{c_tax:.2f}")
                s_entry = etree.SubElement(voucher, "ALLLEDGERENTRIES.LIST")
                _add_element(s_entry, "LEDGERNAME", sgst_ledger)
                _add_element(s_entry, "ISDEEMEDPOSITIVE", "No")
                _add_element(s_entry, "AMOUNT", f"{s_tax:.2f}")

    tree = etree.ElementTree(envelope)
    return etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")
