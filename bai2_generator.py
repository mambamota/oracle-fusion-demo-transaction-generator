import datetime
import random
from typing import List, Dict, Any

class BAI2Generator:
    def __init__(self):
        self.record_types = {
            '01': 'Group Header',
            '02': 'Account Identifier', 
            '03': 'Transaction Detail',
            '16': 'Group Trailer',
            '49': 'Account Trailer',
            '98': 'File Trailer',
            '99': 'Group Trailer'
        }
    
    def generate_bai2_file(self, accounts: List[Dict[str, Any]], transactions_per_account: int = 10, 
                          opening_balance: float = 50000.0, target_closing_balance: float = 75000.0) -> str:
        """Generate BAI2 format bank statement with per-account balances"""
        
        bai2_content = []
        
        # File Header (Record Type 01)
        file_header = self._create_file_header()
        bai2_content.append(file_header)
        
        # For each account
        for account in accounts:
            # Use per-account balances if available, otherwise fall back to global defaults
            account_opening_balance = account.get('opening_balance', opening_balance)
            account_closing_balance = account.get('closing_balance', target_closing_balance)
            
            # Account Identifier (Record Type 02)
            account_header = self._create_account_header(account)
            bai2_content.append(account_header)
            
            # Generate transactions for this account
            transactions = self._generate_transactions_for_account(
                account, transactions_per_account, account_opening_balance, account_closing_balance
            )
            
            # Transaction Details (Record Type 03)
            for transaction in transactions:
                transaction_record = self._create_transaction_record(transaction)
                bai2_content.append(transaction_record)
            
            # Account Trailer (Record Type 49) - use per-account balances
            account_trailer = self._create_account_trailer(account, account_opening_balance, account_closing_balance)
            bai2_content.append(account_trailer)
        
        # File Trailer (Record Type 98)
        file_trailer = self._create_file_trailer()
        bai2_content.append(file_trailer)
        
        return '\n'.join(bai2_content)
    
    def _create_file_header(self) -> str:
        """Create BAI2 file header record"""
        today = datetime.datetime.now()
        return f"01,{today.strftime('%m%d%y')},,{today.strftime('%H%M')},,1,{today.strftime('%m%d%y')},,"
    
    def _create_account_header(self, account: Dict[str, Any]) -> str:
        """Create BAI2 account header record"""
        account_number = account.get('account_number_for_transactions', account.get('account_number', ''))
        return f"02,{account_number},,{account.get('currency', 'USD')},,"
    
    def _create_transaction_record(self, transaction: Dict[str, Any]) -> str:
        """Create BAI2 transaction detail record"""
        amount = transaction['amount']
        transaction_type = transaction['type']
        
        # BAI2 transaction codes
        if transaction_type == 'Credit':
            code = '165'  # Credit
        else:
            code = '475'  # Debit
        
        return f"03,{transaction['date']},{code},{amount:.2f},{transaction['description']},,"
    
    def _create_account_trailer(self, account: Dict[str, Any], opening_balance: float, closing_balance: float) -> str:
        """Create BAI2 account trailer record"""
        return f"49,{opening_balance:.2f},{closing_balance:.2f},,"
    
    def _create_file_trailer(self) -> str:
        """Create BAI2 file trailer record"""
        return "98,,,"
    
    def _generate_transactions_for_account(self, account: Dict[str, Any], count: int, 
                                        opening_balance: float, target_closing_balance: float) -> List[Dict[str, Any]]:
        """Generate realistic transactions for an account"""
        transactions = []
        current_balance = opening_balance
        
        for i in range(count):
            # Calculate target amount to reach closing balance
            remaining_transactions = count - i - 1
            if remaining_transactions > 0:
                target_amount = (target_closing_balance - current_balance) / (remaining_transactions + 1)
            else:
                target_amount = target_closing_balance - current_balance
            
            # Generate transaction
            if target_amount > 0:
                transaction_type = 'Credit'
                amount = min(abs(target_amount), random.uniform(100, 5000))
            else:
                transaction_type = 'Debit'
                amount = min(abs(target_amount), random.uniform(100, 3000))
            
            transaction = {
                'date': f"{(i+1):02d}/01/24",
                'type': transaction_type,
                'amount': round(amount, 2),
                'description': f"Demo {transaction_type.lower()} transaction {i+1:03d}"
            }
            
            transactions.append(transaction)
            
            # Update balance
            if transaction_type == 'Credit':
                current_balance += amount
            else:
                current_balance -= amount
        
        return transactions 