#!/usr/bin/env python3
"""
Step 4 Validation Script - AR Invoices/Receipts
Run this to verify the AR invoice generator works correctly
"""

from ar_invoice_generator import ARInvoiceGenerator
import json

def test_ar_invoice_generator():
    """Test the AR invoice generator functionality"""
    print("🔍 Testing AR Invoice Generator...")
    gen = ARInvoiceGenerator()
    print("✅ Generator initialized")
    
    test_accounts = [
        {'account_name': 'Test Account 1', 'currency': 'USD', 'account_number': '1234567890'},
        {'account_name': 'Test Account 2', 'currency': 'EUR', 'account_number': '0987654321'}
    ]
    
    # Generate AR invoices
    ar_invoices = gen.generate_ar_invoices(
        accounts=test_accounts,
        invoices_per_account=3,
        lines_per_invoice=2,
        date_range_days=7
    )
    print(f"✅ Generated {len(ar_invoices)} AR invoices")
    
    # Generate receipts
    ar_receipts = gen.generate_receipts(
        invoices=ar_invoices,
        receipt_percentage=0.7
    )
    print(f"✅ Generated {len(ar_receipts)} AR receipts")
    
    # Validate invoice structure
    print("\n📋 Invoice Validation:")
    for i, invoice in enumerate(ar_invoices[:3]):  # Show first 3
        header = invoice['header']
        print(f"  Invoice {i+1}:")
        print(f"    ✅ InvoiceId: {header['InvoiceId']}")
        print(f"    ✅ CustomerName: {header['CustomerName']}")
        print(f"    ✅ InvoiceAmount: ${header['InvoiceAmount']:,.2f}")
        print(f"    ✅ Currency: {header['Currency']}")
        print(f"    ✅ PaymentTerms: {header['PaymentTerms']}")
        print(f"    ✅ Lines: {len(invoice['lines'])}")
    
    # Validate receipt structure
    print("\n💰 Receipt Validation:")
    for i, receipt in enumerate(ar_receipts[:3]):  # Show first 3
        print(f"  Receipt {i+1}:")
        print(f"    ✅ ReceiptId: {receipt['ReceiptId']}")
        print(f"    ✅ InvoiceId: {receipt['InvoiceId']}")
        print(f"    ✅ Amount: ${receipt['Amount']:,.2f}")
        print(f"    ✅ PaymentMethod: {receipt['PaymentMethod']}")
        print(f"    ✅ Status: {receipt['Status']}")
    
    # Test CSV generation
    print("\n📄 CSV Content (first 3 lines):")
    csv_content = gen.generate_csv_content(ar_invoices)
    lines = csv_content.split('\n')[:4]
    for line in lines:
        print(f"  {line}")
    
    # Test receipts CSV generation
    if ar_receipts:
        print("\n💰 Receipts CSV Content (first 3 lines):")
        receipts_csv_content = gen.generate_receipts_csv_content(ar_receipts)
        lines = receipts_csv_content.split('\n')[:4]
        for line in lines:
            print(f"  {line}")
    
    # Test Oracle Fusion format
    print("\n🏦 Oracle Fusion Format (first invoice):")
    fusion_format = gen.generate_oracle_fusion_format(ar_invoices)
    if fusion_format:
        first_invoice = fusion_format[0]
        print(json.dumps(first_invoice, indent=2))
    
    # Summary statistics
    print("\n📊 Summary:")
    total_invoice_amount = sum(inv['header']['InvoiceAmount'] for inv in ar_invoices)
    total_receipt_amount = sum(r['Amount'] for r in ar_receipts)
    total_lines = sum(len(inv['lines']) for inv in ar_invoices)
    
    print(f"  Total Invoices: {len(ar_invoices)}")
    print(f"  Total Invoice Amount: ${total_invoice_amount:,.2f}")
    print(f"  Total Receipts: {len(ar_receipts)}")
    print(f"  Total Receipt Amount: ${total_receipt_amount:,.2f}")
    print(f"  Total Line Items: {total_lines}")
    print(f"  Receipt Coverage: {len(ar_receipts)/len(ar_invoices)*100:.1f}%")
    
    print("\n✅ Step 4 Validation Complete!")

if __name__ == "__main__":
    test_ar_invoice_generator() 