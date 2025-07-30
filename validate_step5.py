#!/usr/bin/env python3
"""
Step 5 Validation Script - GL Journals
Run this to verify the GL journal generator works correctly
"""

from gl_journal_generator import GLJournalGenerator
import json

def test_gl_journal_generator():
    """Test the GL journal generator functionality"""
    print("🔍 Testing GL Journal Generator...")
    gen = GLJournalGenerator()
    print("✅ Generator initialized")
    
    test_accounts = [
        {'account_name': 'Test Account 1', 'currency': 'USD', 'account_number': '1234567890'},
        {'account_name': 'Test Account 2', 'currency': 'EUR', 'account_number': '0987654321'}
    ]
    
    # Generate GL journals
    gl_journals = gen.generate_gl_journals(
        accounts=test_accounts,
        journals_per_account=2,
        lines_per_journal=3,
        date_range_days=7
    )
    print(f"✅ Generated {len(gl_journals)} GL journals")
    
    # Validate journal structure
    print("\n📊 Journal Validation:")
    for i, journal in enumerate(gl_journals[:3]):  # Show first 3
        header = journal['header']
        print(f"  Journal {i+1}:")
        print(f"    ✅ JournalId: {header['JournalId']}")
        print(f"    ✅ JournalName: {header['JournalName']}")
        print(f"    ✅ JournalType: {header['JournalType']}")
        print(f"    ✅ BusinessUnit: {header['BusinessUnit']}")
        print(f"    ✅ Ledger: {header['Ledger']}")
        print(f"    ✅ Currency: {header['Currency']}")
        print(f"    ✅ TotalDebit: ${header['TotalDebit']:,.2f}")
        print(f"    ✅ TotalCredit: ${header['TotalCredit']:,.2f}")
        print(f"    ✅ Lines: {len(journal['lines'])}")
        
        # Check if journal is balanced
        if abs(header['TotalDebit'] - header['TotalCredit']) < 0.01:
            print(f"    ✅ Journal is balanced")
        else:
            print(f"    ❌ Journal is NOT balanced!")
    
    # Validate line structure
    print("\n📋 Line Validation:")
    for i, journal in enumerate(gl_journals[:2]):  # Show first 2 journals
        print(f"  Journal {i+1} Lines:")
        for j, line in enumerate(journal['lines']):
            print(f"    Line {j+1}:")
            print(f"      ✅ AccountType: {line['AccountType']}")
            print(f"      ✅ GLAccount: {line['GLAccount']}")
            print(f"      ✅ DebitAmount: ${line['DebitAmount']:,.2f}")
            print(f"      ✅ CreditAmount: ${line['CreditAmount']:,.2f}")
            print(f"      ✅ LineType: {line['LineType']}")
    
    # Test CSV generation
    print("\n📄 CSV Content (first 3 lines):")
    csv_content = gen.generate_csv_content(gl_journals)
    lines = csv_content.split('\n')[:4]
    for line in lines:
        print(f"  {line}")
    
    # Test Oracle Fusion format
    print("\n🏦 Oracle Fusion Format (first journal):")
    fusion_format = gen.generate_oracle_fusion_format(gl_journals)
    if fusion_format:
        first_journal = fusion_format[0]
        print(json.dumps(first_journal, indent=2))
    
    # Test Properties format
    print("\n⚙️ Properties Content (first few lines):")
    properties_content = gen.generate_properties_content(gl_journals)
    lines = properties_content.split('\n')[:10]
    for line in lines:
        print(f"  {line}")
    
    # Summary statistics
    print("\n📊 Summary:")
    total_journals = len(gl_journals)
    total_lines = sum(len(journal['lines']) for journal in gl_journals)
    total_debit = sum(journal['header']['TotalDebit'] for journal in gl_journals)
    total_credit = sum(journal['header']['TotalCredit'] for journal in gl_journals)
    
    print(f"  Total Journals: {total_journals}")
    print(f"  Total Lines: {total_lines}")
    print(f"  Total Debit: ${total_debit:,.2f}")
    print(f"  Total Credit: ${total_credit:,.2f}")
    print(f"  Average Lines per Journal: {total_lines/total_journals:.1f}")
    
    # Check overall balance
    if abs(total_debit - total_credit) < 0.01:
        print(f"  ✅ All journals are balanced!")
    else:
        print(f"  ❌ Journals are NOT balanced!")
    
    print("\n✅ Step 5 Validation Complete!")

if __name__ == "__main__":
    test_gl_journal_generator() 