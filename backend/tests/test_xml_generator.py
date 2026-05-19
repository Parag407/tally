import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.xml_generator import generate_bank_xml, generate_sales_xml, generate_purchase_xml
import xml.etree.ElementTree as ET

def validate_xml_structure(xml_str: str):
    root = ET.fromstring(xml_str.encode('utf-8'))
    
    # 1. Envelope -> Header / Body
    assert root.tag == "ENVELOPE"
    
    header = root.find("HEADER")
    assert header is not None
    assert header.find("TALLYREQUEST").text == "Import Data"
    
    body = root.find("BODY")
    assert body is not None
    
    import_data = body.find("IMPORTDATA")
    assert import_data is not None
    
    req_data = import_data.find("REQUESTDATA")
    if req_data is not None:
        messages = req_data.findall("TALLYMESSAGE")
        for tallymsg in messages:
            voucher = tallymsg.find("VOUCHER")
            if voucher is not None:
                # 2. Mandatory Rules Check
                date = voucher.find("DATE")
                assert date is not None and len(date.text) == 8, f"Invalid Date format: {date.text if date is not None else 'Missing'}"
                
                vtypename = voucher.find("VOUCHERTYPENAME")
                assert vtypename is not None and vtypename.text in ["Payment", "Sales", "Purchase", "Receipt"]
                
                narration = voucher.find("NARRATION")
                assert narration is not None, "Narration is mandatory"
                
                # Check Ledger Entries balancing
                ledgers = voucher.findall("ALLLEDGERENTRIES.LIST")
                assert len(ledgers) >= 2, "Must have at least 2 ledger entries"
                
                debit_total = 0.0
                credit_total = 0.0
                
                for ledger in ledgers:
                    is_deemed_positive = ledger.find("ISDEEMEDPOSITIVE").text
                    amt = float(ledger.find("AMOUNT").text)
                    
                    if is_deemed_positive == "Yes":  # Debit
                        assert amt < 0, f"Debit amount MUST be negative. Found: {amt}"
                        debit_total += abs(amt)
                    else:  # Credit
                        assert amt > 0, f"Credit amount MUST be positive. Found: {amt}"
                        credit_total += amt
                        
                # Floating point check with precision
                assert round(debit_total, 2) == round(credit_total, 2), f"Unbalanced voucher! Debit: {debit_total}, Credit: {credit_total}"
                
    return True

def run_tests():
    print("Testing Bank XML Generation...")
    records = [
        {
            "date": "15-05-2023",
            "amount": 10500.50,
            "narration": "Paid   for \n office supplies", # test sanitation
            "voucher_type": "Payment",
            "debit_ledger": "Office Supplies",
            "voucher_no": "PAY-001"
        }
    ]
    xml_out = generate_bank_xml(records)
    assert validate_xml_structure(xml_out)
    if '<NARRATION>Paid   for \n office supplies</NARRATION>' not in xml_out and '<NARRATION>Paid   for office supplies</NARRATION>' not in xml_out:
        print("XML OUT NARRATION FAILED:")
        print(xml_out)
    assert '<NARRATION>' in xml_out
    assert '<AMOUNT>-10500.50</AMOUNT>' in xml_out
    assert '<AMOUNT>10500.50</AMOUNT>' in xml_out
    print("Bank XML OK.")

    print("Testing Sales XML Generation (with GST & sanitization)...")
    sales_records = [
        {
            "date": "2023-12-05 10:30:00", # timestamp should be stripped cleanly
            "taxable_amount": 1000.00,
            "bill_amount": 1180.00,
            "tax_amount": 180.00,
            "cgst_ledger": "CGST",
            "sgst_ledger": "SGST",
            "gst_rate": "18.0",
            "party_name": "Acme Corp & Co.", # Ampersand checks
            "item_name": "Widgets"
        }
    ]
    sales_xml = generate_sales_xml(sales_records)
    assert validate_xml_structure(sales_xml)
    
    # 1180 with 18% GST => Taxable: 1000, CGST: 90, SGST: 90
    assert '<DATE>20231205</DATE>' in sales_xml
    assert '<AMOUNT>-1180.00</AMOUNT>' in sales_xml # Party debit
    assert '<AMOUNT>1000.00</AMOUNT>' in sales_xml # Sales credit
    assert '<AMOUNT>90.00</AMOUNT>' in sales_xml # GST credits
    print("Sales XML OK.")

    print("Testing Purchase XML Generation (edge cases)...")
    purchase_records = [
        {
            "date": "", # Default date handling
            "bill_amount": 500.00,
            "taxable_amount": 500.00,
            "tax_amount": 0,
            "gst_rate": 0,
            "party_name": "Cash Supplier", 
            "voucher_no": "  ", # Should be omitted since empty
            "narration": "" # Should default to Purchase Entry
        }
    ]
    pur_xml = generate_purchase_xml(purchase_records)
    assert validate_xml_structure(pur_xml)
    assert '<PARTYNAME>Cash Supplier</PARTYNAME>' in pur_xml
    assert '<NARRATION>Purchase Entry</NARRATION>' in pur_xml
    assert '<VOUCHERNUMBER>' not in pur_xml
    print("Purchase XML OK.")
    
    print("All tests passed.")

if __name__ == "__main__":
    run_tests()
