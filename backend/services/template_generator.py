"""
Template Generator Service
Creates sample Excel templates for each voucher type.
"""
import io
import xlsxwriter


def create_bank_template() -> bytes:
    """Generate sample Excel template for bank vouchers."""
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})
    ws = wb.add_worksheet("Bank Template")

    # Formats
    header_fmt = wb.add_format({
        "bold": True,
        "bg_color": "#1a56db",
        "font_color": "#ffffff",
        "border": 1,
        "text_wrap": True,
        "align": "center",
        "valign": "vcenter",
    })
    cell_fmt = wb.add_format({"border": 1, "align": "center", "valign": "vcenter"})
    date_fmt = wb.add_format({"border": 1, "align": "center", "valign": "vcenter", "num_format": "dd-mm-yyyy"})

    headers = ["DATE", "VOUCHER NO (Optional)", "BY - DR", "TO - CR", "AMOUNT", "NARRATION", "TYPE"]
    widths = [15, 15, 20, 20, 15, 30, 12]

    for i, (h, w) in enumerate(zip(headers, widths)):
        ws.set_column(i, i, w)
        ws.write(0, i, h, header_fmt)

    # Sample data
    sample = [
        ["01-04-2025", "V001", "Rent Expense", "HDFC Bank", 15000, "Office rent April", "Payment"],
        ["02-04-2025", "V002", "HDFC Bank", "Sales Revenue", 50000, "Client payment received", "Receipt"],
        ["05-04-2025", "V003", "Electricity", "HDFC Bank", 3500, "Electricity bill", "Payment"],
    ]
    for r, row in enumerate(sample, 1):
        for c, val in enumerate(row):
            ws.write(r, c, val, date_fmt if c == 0 else cell_fmt)

    # Instructions sheet
    inst = wb.add_worksheet("Instructions")
    inst.set_column(0, 0, 60)
    inst_fmt = wb.add_format({"text_wrap": True, "valign": "top"})
    title_fmt = wb.add_format({"bold": True, "font_size": 14})

    inst.write(0, 0, "Bank Voucher Template - Instructions", title_fmt)
    instructions = [
        "1. DATE: Use DD-MM-YYYY format (e.g., 01-04-2025)",
        "2. VOUCHER NO (Optional): Unique voucher reference number",
        "3. BY - DR: Debit ledger name (account being debited)",
        "4. TO - CR: Credit ledger name (account being credited)",
        "5. AMOUNT: Transaction amount (numeric, no commas)",
        "6. NARRATION: Description of the transaction",
        "7. TYPE: 'Payment' or 'Receipt'",
        "",
        "Note: All ledger names must match Tally ledger names exactly.",
    ]
    for i, line in enumerate(instructions, 2):
        inst.write(i, 0, line, inst_fmt)

    wb.close()
    output.seek(0)
    return output.read()


def create_sales_template() -> bytes:
    """Generate sample Excel template for sales vouchers."""
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})
    ws = wb.add_worksheet("Sales Template")

    header_fmt = wb.add_format({
        "bold": True,
        "bg_color": "#047857",
        "font_color": "#ffffff",
        "border": 1,
        "text_wrap": True,
        "align": "center",
        "valign": "vcenter",
    })
    cell_fmt = wb.add_format({"border": 1, "align": "center", "valign": "vcenter"})

    headers = ["DATE", "INVOICE NO", "CASH/PARTY", "PURCHASE/SALES LEDGER", "IGST/CENTRAL GST LEDGER", "UT/STATE GST LEDGER", "TAXABLE AMOUNT", "NARRATION", "GST SLAB", "GST", "BILL AMOUNT", "PLACE OF SUPPLY", "TYPE"]
    widths = [12, 18, 25, 25, 20, 20, 15, 30, 10, 12, 15, 15, 10]

    for i, (h, w) in enumerate(zip(headers, widths)):
        ws.set_column(i, i, w)
        ws.write(0, i, h, header_fmt)

    sample = [
        ["04-05-2025", "E/SL/25-26/87", "RAGHUVEER ENTERPRISES", "Sales GST @ 28% M", "CGST @ 14% (S)", "SGST @ 14% (S)", 76234.38, "Sales made", "28%", 21345.63, 97580.01, "Maharashtra", "Sales"],
        ["08-05-2025", "E/SL/25-26/99", "RAGHUVEER ENTERPRISES", "Sales GST @ 28% M", "CGST @ 14% (S)", "SGST @ 14% (S)", 74953.13, "Sales made", "28%", 20986.88, 95940.01, "Maharashtra", "Sales"],
    ]
    for r, row in enumerate(sample, 1):
        for c, val in enumerate(row):
            ws.write(r, c, val, cell_fmt)

    # Instructions
    inst = wb.add_worksheet("Instructions")
    inst.set_column(0, 0, 60)
    inst_fmt = wb.add_format({"text_wrap": True, "valign": "top"})
    title_fmt = wb.add_format({"bold": True, "font_size": 14})

    inst.write(0, 0, "Sales Voucher Template - Instructions", title_fmt)
    instructions = [
        "1. DATE: Use DD-MM-YYYY format",
        "2. VOUCHER NO (Optional): Unique invoice number",
        "3. PARTY NAME: Customer/Buyer name (must match Tally ledger)",
        "4. ITEM NAME: Stock item name (must match Tally stock item)",
        "5. QUANTITY: Number of units sold",
        "6. RATE: Price per unit",
        "7. AMOUNT: Total amount (Rate × Quantity) including GST",
        "8. GST RATE: GST percentage (e.g., 18 for 18%)",
        "9. HSN CODE: HSN/SAC code for the item",
        "10. NARRATION: Description of the sale",
    ]
    for i, line in enumerate(instructions, 2):
        inst.write(i, 0, line, inst_fmt)

    wb.close()
    output.seek(0)
    return output.read()


def create_purchase_template() -> bytes:
    """Generate sample Excel template for purchase vouchers."""
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})
    ws = wb.add_worksheet("Purchase Template")

    header_fmt = wb.add_format({
        "bold": True,
        "bg_color": "#b91c1c",
        "font_color": "#ffffff",
        "border": 1,
        "text_wrap": True,
        "align": "center",
        "valign": "vcenter",
    })
    cell_fmt = wb.add_format({"border": 1, "align": "center", "valign": "vcenter"})

    headers = ["DATE", "INVOICE NO", "CASH/PARTY", "PURCHASE/SALES LEDGER", "IGST/CENTRAL GST LEDGER", "UT/STATE GST LEDGER", "TAXABLE AMOUNT", "NARRATION", "GST SLAB", "GST", "BILL AMOUNT", "PLACE OF SUPPLY", "TYPE"]
    widths = [12, 18, 25, 25, 20, 20, 15, 30, 10, 12, 15, 15, 10]

    for i, (h, w) in enumerate(zip(headers, widths)):
        ws.set_column(i, i, w)
        ws.write(0, i, h, header_fmt)

    sample = [
        ["04-05-2025", "P/25-26/01", "SUPPLIER NAME", "Purchase GST @ 18% M", "CGST @ 9% (S)", "SGST @ 9% (S)", 50000.00, "Purchase made", "18%", 9000.00, 59000.00, "Maharashtra", "Purchase"],
    ]
    for r, row in enumerate(sample, 1):
        for c, val in enumerate(row):
            ws.write(r, c, val, cell_fmt)

    # Instructions
    inst = wb.add_worksheet("Instructions")
    inst.set_column(0, 0, 60)
    inst_fmt = wb.add_format({"text_wrap": True, "valign": "top"})
    title_fmt = wb.add_format({"bold": True, "font_size": 14})

    inst.write(0, 0, "Purchase Voucher Template - Instructions", title_fmt)
    instructions = [
        "1. DATE: Use DD-MM-YYYY format",
        "2. VOUCHER NO (Optional): Unique purchase invoice number",
        "3. PARTY NAME: Supplier/Vendor name (must match Tally ledger)",
        "4. ITEM NAME: Stock item name (must match Tally stock item)",
        "5. QUANTITY: Number of units purchased",
        "6. RATE: Price per unit",
        "7. AMOUNT: Total amount (Rate × Quantity) including GST",
        "8. GST RATE: GST percentage (e.g., 18 for 18%)",
        "9. HSN CODE: HSN/SAC code for the item",
        "10. NARRATION: Description of the purchase",
    ]
    for i, line in enumerate(instructions, 2):
        inst.write(i, 0, line, inst_fmt)

    wb.close()
    output.seek(0)
    return output.read()


def create_debit_note_template() -> bytes:
    """Generate sample Excel template for Debit Note vouchers."""
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})
    ws = wb.add_worksheet("Debit Note Template")

    header_fmt = wb.add_format({
        "bold": True,
        "bg_color": "#7c3aed",   # Violet – distinct from sales/purchase
        "font_color": "#ffffff",
        "border": 1,
        "text_wrap": True,
        "align": "center",
        "valign": "vcenter",
    })
    cell_fmt = wb.add_format({"border": 1, "align": "center", "valign": "vcenter"})
    note_fmt = wb.add_format({"border": 1, "align": "center", "valign": "vcenter", "italic": True, "font_color": "#6b7280"})

    headers = [
        "DATE", "VOUCHER NO", "PARTY NAME", "GSTIN",
        "RETURN LEDGER", "IGST/CENTRAL GST LEDGER", "UT/STATE GST LEDGER", "IGST LEDGER",
        "TAXABLE AMOUNT", "CGST %", "SGST %", "IGST %",
        "TAX AMOUNT", "TOTAL AMOUNT", "REASON",
    ]
    widths = [14, 16, 25, 20, 25, 22, 22, 18, 16, 9, 9, 9, 14, 14, 30]

    for i, (h, w) in enumerate(zip(headers, widths)):
        ws.set_column(i, i, w)
        ws.write(0, i, h, header_fmt)

    sample = [
        [
            "05-04-2025", "DN/25-26/001", "SUPPLIER ENTERPRISES", "27ABCDE1234F1Z5",
            "Purchase Return Account", "CGST @ 9% (S)", "SGST @ 9% (S)", "",
            50000.00, 9, 9, 0,
            9000.00, 59000.00, "Goods returned – damaged material",
        ],
        [
            "10-04-2025", "DN/25-26/002", "ABC TRADERS", "27XYZAB5678G1Z1",
            "Purchase Return Account", "", "", "IGST @ 18% (S)",
            30000.00, 0, 0, 18,
            5400.00, 35400.00, "Price difference credit",
        ],
    ]
    for r, row in enumerate(sample, 1):
        for c, val in enumerate(row):
            ws.write(r, c, val, cell_fmt)

    # Instructions sheet
    inst = wb.add_worksheet("Instructions")
    inst.set_column(0, 0, 65)
    inst_fmt = wb.add_format({"text_wrap": True, "valign": "top"})
    title_fmt = wb.add_format({"bold": True, "font_size": 14, "font_color": "#7c3aed"})

    inst.write(0, 0, "Debit Note Template – Instructions", title_fmt)
    instructions = [
        "1.  DATE          : Use DD-MM-YYYY format (e.g., 05-04-2025)",
        "2.  VOUCHER NO    : Unique Debit Note reference number (required)",
        "3.  PARTY NAME    : Supplier / Vendor name (must match Tally ledger exactly)",
        "4.  GSTIN         : GSTIN of the party (optional, for reference)",
        "5.  RETURN LEDGER : Tally ledger name for Purchase Return (e.g., 'Purchase Return Account')",
        "6.  CGST LEDGER   : Tally ledger for CGST — leave blank if IGST applies",
        "7.  SGST LEDGER   : Tally ledger for SGST — leave blank if IGST applies",
        "8.  IGST LEDGER   : Tally ledger for IGST — leave blank if CGST/SGST applies",
        "9.  TAXABLE AMOUNT: Base amount before tax (numeric, no commas)",
        "10. CGST %        : CGST rate as a plain number (e.g., 9 for 9%) — 0 if IGST",
        "11. SGST %        : SGST rate as a plain number — 0 if IGST",
        "12. IGST %        : IGST rate as a plain number — 0 if CGST/SGST",
        "13. TAX AMOUNT    : Total GST amount (or leave 0 — will be computed from %)",
        "14. TOTAL AMOUNT  : Taxable Amount + Tax Amount",
        "15. REASON        : Reason for issuing the Debit Note",
        "",
        "NOTE: Either fill CGST%+SGST% OR IGST%, not both.",
        "NOTE: All ledger names must match Tally ledgers exactly (case-sensitive).",
    ]
    for i, line in enumerate(instructions, 2):
        inst.write(i, 0, line, inst_fmt)

    wb.close()
    output.seek(0)
    return output.read()


def create_credit_note_template() -> bytes:
    """Generate sample Excel template for Credit Note vouchers."""
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})
    ws = wb.add_worksheet("Credit Note Template")

    header_fmt = wb.add_format({
        "bold": True,
        "bg_color": "#0891b2",   # Cyan – distinct from debit note
        "font_color": "#ffffff",
        "border": 1,
        "text_wrap": True,
        "align": "center",
        "valign": "vcenter",
    })
    cell_fmt = wb.add_format({"border": 1, "align": "center", "valign": "vcenter"})

    headers = [
        "DATE", "VOUCHER NO", "PARTY NAME", "GSTIN",
        "RETURN LEDGER", "IGST/CENTRAL GST LEDGER", "UT/STATE GST LEDGER", "IGST LEDGER",
        "TAXABLE AMOUNT", "CGST %", "SGST %", "IGST %",
        "TAX AMOUNT", "TOTAL AMOUNT", "REASON",
    ]
    widths = [14, 16, 25, 20, 25, 22, 22, 18, 16, 9, 9, 9, 14, 14, 30]

    for i, (h, w) in enumerate(zip(headers, widths)):
        ws.set_column(i, i, w)
        ws.write(0, i, h, header_fmt)

    sample = [
        [
            "06-04-2025", "CN/25-26/001", "CUSTOMER ABC PVT LTD", "27PQRST6789H1Z3",
            "Sales Return Account", "CGST @ 14% (S)", "SGST @ 14% (S)", "",
            76234.38, 14, 14, 0,
            21345.63, 97580.01, "Goods returned by customer",
        ],
        [
            "12-04-2025", "CN/25-26/002", "RAGHUVEER ENTERPRISES", "27ABCDE1234F1Z5",
            "Sales Return Account", "", "", "IGST @ 18% (S)",
            40000.00, 0, 0, 18,
            7200.00, 47200.00, "Price adjustment – overcharged",
        ],
    ]
    for r, row in enumerate(sample, 1):
        for c, val in enumerate(row):
            ws.write(r, c, val, cell_fmt)

    # Instructions sheet
    inst = wb.add_worksheet("Instructions")
    inst.set_column(0, 0, 65)
    inst_fmt = wb.add_format({"text_wrap": True, "valign": "top"})
    title_fmt = wb.add_format({"bold": True, "font_size": 14, "font_color": "#0891b2"})

    inst.write(0, 0, "Credit Note Template – Instructions", title_fmt)
    instructions = [
        "1.  DATE          : Use DD-MM-YYYY format (e.g., 06-04-2025)",
        "2.  VOUCHER NO    : Unique Credit Note reference number (required)",
        "3.  PARTY NAME    : Customer / Buyer name (must match Tally ledger exactly)",
        "4.  GSTIN         : GSTIN of the party (optional, for reference)",
        "5.  RETURN LEDGER : Tally ledger name for Sales Return (e.g., 'Sales Return Account')",
        "6.  CGST LEDGER   : Tally ledger for CGST — leave blank if IGST applies",
        "7.  SGST LEDGER   : Tally ledger for SGST — leave blank if IGST applies",
        "8.  IGST LEDGER   : Tally ledger for IGST — leave blank if CGST/SGST applies",
        "9.  TAXABLE AMOUNT: Base amount before tax (numeric, no commas)",
        "10. CGST %        : CGST rate as a plain number (e.g., 14 for 14%) — 0 if IGST",
        "11. SGST %        : SGST rate as a plain number — 0 if IGST",
        "12. IGST %        : IGST rate as a plain number — 0 if CGST/SGST",
        "13. TAX AMOUNT    : Total GST amount (or leave 0 — will be computed from %)",
        "14. TOTAL AMOUNT  : Taxable Amount + Tax Amount",
        "15. REASON        : Reason for issuing the Credit Note",
        "",
        "NOTE: Either fill CGST%+SGST% OR IGST%, not both.",
        "NOTE: All ledger names must match Tally ledgers exactly (case-sensitive).",
    ]
    for i, line in enumerate(instructions, 2):
        inst.write(i, 0, line, inst_fmt)

    wb.close()
    output.seek(0)
    return output.read()
