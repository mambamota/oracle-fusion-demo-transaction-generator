import random
import datetime
from typing import List, Dict, Any

class ExternalCashGenerator:
    def __init__(self):
        self.transaction_types = ['CHK', 'EFT', 'MSC', 'WIR', 'ACH']
        self.business_units = ['US1 Business Unit', 'UK Business Unit', 'CA Business Unit']
        self.currencies = ['USD', 'CAD', 'EUR', 'GBP']
        
    def generate_external_transactions(self, accounts: List[Dict[str, Any]], 
                                    transactions_per_account: int = 5,
                                    date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Generate external cash transactions for Oracle Fusion"""
        
        transactions = []
        base_date = datetime.datetime.now()
        
        for account in accounts:
            account_name = account.get('account_name', 'Unknown Account')
            currency = account.get('currency', 'USD')
            
            for i in range(transactions_per_account):
                # Generate random transaction date within range
                days_offset = random.randint(0, date_range_days)
                transaction_date = base_date - datetime.timedelta(days=days_offset)
                
                # Generate transaction
                transaction = {
                    'BankAccountName': account_name,
                    'Amount': self._generate_amount(currency),
                    'TransactionDate': transaction_date.strftime('%m/%d/%Y'),
                    'TransactionType': random.choice(self.transaction_types),
                    'Reference': f"EXT-{account_name[:3]}-{i+1:02d}{chr(65 + i % 26)}",
                    'BusinessUnit': random.choice(self.business_units),
                    'Reconciled': 'Y' if random.random() > 0.3 else 'N'  # 70% reconciled
                }
                
                transactions.append(transaction)
        
        return transactions
    
    def _generate_amount(self, currency: str) -> float:
        """Generate realistic transaction amounts"""
        # Different amount ranges based on currency
        if currency == 'USD':
            base_range = (100, 10000)
        elif currency == 'CAD':
            base_range = (150, 15000)
        elif currency == 'EUR':
            base_range = (80, 8000)
        else:  # GBP
            base_range = (70, 7000)
        
        # 70% positive (credits), 30% negative (debits)
        is_credit = random.random() > 0.3
        amount = random.uniform(base_range[0], base_range[1])
        
        return round(amount, 2) if is_credit else round(-amount, 2)
    
    def generate_csv_content(self, transactions: List[Dict[str, Any]]) -> str:
        """Generate CSV content for external transactions"""
        if not transactions:
            return ""
        
        # CSV header
        csv_lines = ['BankAccountName,Amount,TransactionDate,TransactionType,Reference,BusinessUnit,Reconciled']
        
        # CSV data rows
        for transaction in transactions:
            csv_line = f"{transaction['BankAccountName']},{transaction['Amount']},{transaction['TransactionDate']},{transaction['TransactionType']},{transaction['Reference']},{transaction['BusinessUnit']},{transaction['Reconciled']}"
            csv_lines.append(csv_line)
        
        return '\n'.join(csv_lines)
    
    def generate_oracle_fusion_format(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate Oracle Fusion API format for posting"""
        fusion_transactions = []
        
        for transaction in transactions:
            fusion_transaction = {
                'bankAccountName': transaction['BankAccountName'],
                'amount': transaction['Amount'],
                'transactionDate': transaction['TransactionDate'],
                'transactionType': transaction['TransactionType'],
                'reference': transaction['Reference'],
                'businessUnit': transaction['BusinessUnit'],
                'reconciled': transaction['Reconciled'] == 'Y',
                'currency': 'USD',  # Default, could be enhanced
                'description': f"External {transaction['TransactionType']} transaction",
                'source': 'External Cash Management'
            }
            fusion_transactions.append(fusion_transaction)
        
        return fusion_transactions 