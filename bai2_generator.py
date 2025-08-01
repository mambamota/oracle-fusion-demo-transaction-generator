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
                          opening_balance: float = 50000.0, target_closing_balance: float = 75000.0,
                          pre_generated_transactions: List[Dict[str, Any]] = None) -> str:
        """Generate BAI2 format bank statement with per-account balances"""
        
        # Validate inputs
        if not accounts:
            raise ValueError("No accounts provided for BAI2 generation")
        
        bai2_content = []
        
        # File Header (Record Type 01)
        file_header = self._create_file_header()
        bai2_content.append(file_header)
        
        # For each account
        for account in accounts:
            try:
                # Use per-account balances if available, otherwise fall back to global defaults
                account_opening_balance = account.get('opening_balance', opening_balance)
                account_closing_balance = account.get('closing_balance', target_closing_balance)
                
                # Account Identifier (Record Type 02)
                account_header = self._create_account_header(account)
                bai2_content.append(account_header)
                
                # Get transactions for this account
                if pre_generated_transactions:
                    # Use pre-generated transactions for this account
                    account_transactions = [t for t in pre_generated_transactions if t.get('account_id') == account.get('account_id')]
                else:
                    # Fallback to generating transactions (for backward compatibility)
                    account_transactions = self._generate_transactions_for_account(
                        account, transactions_per_account, account_opening_balance, account_closing_balance
                    )
                
                # Transaction Details (Record Type 03)
                for transaction in account_transactions:
                    transaction_record = self._create_transaction_record(transaction)
                    bai2_content.append(transaction_record)
                
                # Account Trailer (Record Type 49) - use per-account balances
                account_trailer = self._create_account_trailer(account, account_opening_balance, account_closing_balance)
                bai2_content.append(account_trailer)
                
            except Exception as e:
                # Log error but continue with other accounts
                print(f"Error processing account {account.get('account_id', 'unknown')}: {e}")
                continue
        
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
        try:
            amount = transaction.get('amount', 0.0)
            transaction_type = transaction.get('type', 'Credit')
            
            # Convert date format from YYYY-MM-DD to DD/MM/YY
            date_str = transaction.get('date', '01/01/24')
            if '-' in date_str:
                # Parse YYYY-MM-DD format
                from datetime import datetime
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    date_formatted = date_obj.strftime('%d/%m/%y')
                except ValueError:
                    # Fallback to default date
                    date_formatted = '01/01/24'
            else:
                # Assume already in DD/MM/YY format
                date_formatted = date_str
            
            # BAI2 transaction codes - more realistic codes
            if transaction_type == 'Credit':
                # Various credit codes
                credit_codes = ['165', '195', '200', '210', '220']  # Different credit types
                code = credit_codes[hash(str(transaction.get('description', ''))) % len(credit_codes)]
            else:
                # Various debit codes
                debit_codes = ['475', '485', '490', '500', '510']  # Different debit types
                code = debit_codes[hash(str(transaction.get('description', ''))) % len(debit_codes)]
            
            # Truncate description if too long for BAI2 format
            description = transaction.get('description', 'Demo transaction')
            if len(description) > 30:
                description = description[:27] + "..."
            
            return f"03,{date_formatted},{code},{amount:.2f},{description},,"
            
        except Exception as e:
            # Return a safe default transaction record
            print(f"Error creating transaction record: {e}")
            return f"03,01/01/24,165,0.00,Demo transaction,,"
    
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