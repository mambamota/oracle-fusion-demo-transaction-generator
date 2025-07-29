"""
BAI2 Bank Statement Generator
Generates BAI2 format bank statements with opening/closing balances and random transactions
"""

import random
import datetime
from typing import List, Dict, Any
from faker import Faker
import yaml

class BAI2Generator:
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize BAI2 generator
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.fake = Faker()
        self.transactions = []
        self.opening_balance = 0.0
        self.closing_balance = 0.0
        
    def generate_bank_accounts(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate random bank accounts
        
        Args:
            count: Number of accounts to generate
            
        Returns:
            List of bank account dictionaries
        """
        accounts = []
        for i in range(count):
            account = {
                'account_number': self.fake.bban(),
                'routing_number': self.fake.aba(),
                'account_name': f"Demo Account {i+1}",
                'currency': 'USD',
                'opening_balance': random.uniform(10000, 100000),
                'closing_balance': 0.0
            }
            accounts.append(account)
        return accounts
    
    def generate_transactions(self, account: Dict[str, Any], transaction_count: int) -> List[Dict[str, Any]]:
        """
        Generate random transactions for an account
        
        Args:
            account: Bank account dictionary
            transaction_count: Number of transactions to generate
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        current_balance = account['opening_balance']
        
        # Generate transaction types
        transaction_types = ['CREDIT', 'DEBIT']
        descriptions = [
            'Payment received', 'Check payment', 'Wire transfer',
            'Direct deposit', 'ATM withdrawal', 'Online payment',
            'Service charge', 'Interest earned', 'Fee charged'
        ]
        
        for i in range(transaction_count):
            # Random date within last 30 days
            transaction_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Random amount
            amount = random.uniform(
                self.config['transactions']['bank_statement']['min_amount'],
                self.config['transactions']['bank_statement']['max_amount']
            )
            
            # Random transaction type
            transaction_type = random.choice(transaction_types)
            
            # Adjust balance based on transaction type
            if transaction_type == 'CREDIT':
                current_balance += amount
            else:
                current_balance -= amount
            
            transaction = {
                'date': transaction_date.strftime('%Y%m%d'),
                'type': transaction_type,
                'amount': round(amount, 2),
                'reference': f"REF{random.randint(100000, 999999)}",
                'description': random.choice(descriptions),
                'running_balance': round(current_balance, 2)
            }
            
            transactions.append(transaction)
        
        # Update closing balance
        account['closing_balance'] = round(current_balance, 2)
        
        return transactions
    
    def format_bai2_record(self, record_type: str, data: Dict[str, Any]) -> str:
        """
        Format a BAI2 record according to specification
        
        Args:
            record_type: BAI2 record type (01, 02, 03, etc.)
            data: Record data dictionary
            
        Returns:
            Formatted BAI2 record string
        """
        if record_type == "01":  # Group Header
            return f"01,{data.get('sender_id', 'DEMO')},{data.get('receiver_id', 'DEMO')},{data.get('group_date', datetime.datetime.now().strftime('%Y%m%d'))},0001,0001,80,"
        
        elif record_type == "02":  # Account Identifier
            return f"02,{data.get('account_number', '')},{data.get('currency', 'USD')},{data.get('opening_balance', '0.00')},{data.get('closing_balance', '0.00')},"
        
        elif record_type == "03":  # Transaction Detail
            return f"03,{data.get('type', '')},{data.get('amount', '0.00')},{data.get('date', '')},{data.get('reference', '')},{data.get('description', '')},"
        
        elif record_type == "49":  # Account Trailer
            return f"49,{data.get('transaction_count', '0')},{data.get('total_debits', '0.00')},{data.get('total_credits', '0.00')},"
        
        elif record_type == "98":  # File Trailer
            return f"98,{data.get('group_count', '1')},{data.get('total_records', '0')},"
        
        elif record_type == "99":  # Group Trailer
            return f"99,{data.get('total_accounts', '1')},{data.get('total_records', '0')},"
        
        return ""
    
    def generate_bai2_file(self, accounts: List[Dict[str, Any]], output_file: str = None) -> str:
        """
        Generate complete BAI2 file
        
        Args:
            accounts: List of bank accounts with transactions
            output_file: Output file path (optional)
            
        Returns:
            Generated BAI2 file content
        """
        if output_file is None:
            output_file = self.config['output']['bai2_file']
        
        bai2_content = []
        
        # File Header (01)
        header_data = {
            'sender_id': 'DEMO',
            'receiver_id': 'DEMO',
            'group_date': datetime.datetime.now().strftime('%Y%m%d')
        }
        bai2_content.append(self.format_bai2_record("01", header_data))
        
        total_records = 1  # Start with header
        
        for account in accounts:
            # Account Identifier (02)
            account_data = {
                'account_number': account['account_number'],
                'currency': account['currency'],
                'opening_balance': f"{account['opening_balance']:.2f}",
                'closing_balance': f"{account['closing_balance']:.2f}"
            }
            bai2_content.append(self.format_bai2_record("02", account_data))
            total_records += 1
            
            # Transaction Details (03)
            transaction_count = 0
            total_debits = 0.0
            total_credits = 0.0
            
            for transaction in account.get('transactions', []):
                transaction_data = {
                    'type': transaction['type'],
                    'amount': f"{transaction['amount']:.2f}",
                    'date': transaction['date'],
                    'reference': transaction['reference'],
                    'description': transaction['description']
                }
                bai2_content.append(self.format_bai2_record("03", transaction_data))
                total_records += 1
                transaction_count += 1
                
                if transaction['type'] == 'DEBIT':
                    total_debits += transaction['amount']
                else:
                    total_credits += transaction['amount']
            
            # Account Trailer (49)
            trailer_data = {
                'transaction_count': str(transaction_count),
                'total_debits': f"{total_debits:.2f}",
                'total_credits': f"{total_credits:.2f}"
            }
            bai2_content.append(self.format_bai2_record("49", trailer_data))
            total_records += 1
        
        # File Trailer (98)
        file_trailer_data = {
            'group_count': '1',
            'total_records': str(total_records)
        }
        bai2_content.append(self.format_bai2_record("98", file_trailer_data))
        
        # Group Trailer (99)
        group_trailer_data = {
            'total_accounts': str(len(accounts)),
            'total_records': str(total_records)
        }
        bai2_content.append(self.format_bai2_record("99", group_trailer_data))
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(bai2_content))
        
        return output_file
    
    def generate_demo_bank_statement(self, account_count: int = 3, transactions_per_account: int = None) -> str:
        """
        Generate a complete demo bank statement
        
        Args:
            account_count: Number of bank accounts to generate
            transactions_per_account: Number of transactions per account
            
        Returns:
            Path to generated BAI2 file
        """
        if transactions_per_account is None:
            transactions_per_account = self.config['transactions']['bank_statement']['default_count']
        
        # Generate accounts
        accounts = self.generate_bank_accounts(account_count)
        
        # Generate transactions for each account
        for account in accounts:
            account['transactions'] = self.generate_transactions(account, transactions_per_account)
        
        # Generate BAI2 file
        output_file = self.generate_bai2_file(accounts)
        
        return output_file 