#!/usr/bin/env python3
"""
Step 2 Validation Script - External Cash Transactions
Run this to verify the external cash generator works correctly
"""

from external_cash_generator import ExternalCashGenerator
import json

def test_external_cash_generator():
    """Test the external cash generator functionality"""
    print("🔍 Testing External Cash Generator...")
    
    # Initialize generator
    gen = ExternalCashGenerator()
    print("✅ Generator initialized")
    
    # Test data
    test_accounts = [
        {
            'account_name': 'Test Account 1',
            'currency': 'USD',
            'account_number': '1234567890'
        },
        {
            'account_name': 'Test Account 2', 
            'currency': 'EUR',
            'account_number': '0987654321'
        }
    ]
    
    # Generate transactions
    transactions = gen.generate_external_transactions(
        accounts=test_accounts,
        transactions_per_account=3,
        date_range_days=7
    )
    
    print(f"✅ Generated {len(transactions)} transactions")
    
    # Validate transaction structure
    required_fields = ['BankAccountName', 'Amount', 'TransactionDate', 'TransactionType', 'Reference', 'BusinessUnit', 'Reconciled']
    
    for i, transaction in enumerate(transactions):
        print(f"\n📋 Transaction {i+1}:")
        for field in required_fields:
            if field in transaction:
                print(f"  ✅ {field}: {transaction[field]}")
            else:
                print(f"  ❌ Missing field: {field}")
    
    # Test CSV generation
    csv_content = gen.generate_csv_content(transactions)
    print(f"\n📄 CSV Content (first 3 lines):")
    lines = csv_content.split('\n')[:3]
    for line in lines:
        print(f"  {line}")
    
    # Test Oracle Fusion format
    fusion_format = gen.generate_oracle_fusion_format(transactions)
    print(f"\n🏦 Oracle Fusion Format (first transaction):")
    if fusion_format:
        print(json.dumps(fusion_format[0], indent=2))
    
    # Summary statistics
    total_amount = sum(t['Amount'] for t in transactions)
    credit_count = len([t for t in transactions if t['Amount'] > 0])
    debit_count = len([t for t in transactions if t['Amount'] < 0])
    
    print(f"\n📊 Summary:")
    print(f"  Total Amount: ${total_amount:,.2f}")
    print(f"  Credit Transactions: {credit_count}")
    print(f"  Debit Transactions: {debit_count}")
    
    print("\n✅ Step 2 Validation Complete!")

if __name__ == "__main__":
    test_external_cash_generator() 