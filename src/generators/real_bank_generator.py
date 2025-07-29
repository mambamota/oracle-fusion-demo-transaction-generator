"""
Real Bank Account Generator
Uses real bank account information from Oracle Fusion with fake transactions
"""

import random
import datetime
from typing import List, Dict, Any, Optional
from faker import Faker
import yaml

class RealBankGenerator:
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize real bank generator
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.fake = Faker()
    
    def process_real_bank_accounts(self, bank_accounts_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process real bank accounts from Oracle Fusion API
        
        Args:
            bank_accounts_data: Response from Oracle Fusion API
            
        Returns:
            List of processed bank accounts
        """
        processed_accounts = []
        
        try:
            # Extract accounts from the API response
            accounts = bank_accounts_data.get('items', [])
            
            for account in accounts:
                processed_account = {
                    'account_id': account.get('AccountId'),
                    'account_name': account.get('AccountName', 'Unknown Account'),
                    'account_number': account.get('AccountNumber', ''),
                    'currency': account.get('CurrencyCode', 'USD'),
                    'bank_name': account.get('BankName', 'Unknown Bank'),
                    'bank_branch': account.get('BankBranchName', ''),
                    'legal_entity': account.get('LegalEntityName', ''),
                    'country': account.get('CountryCode', 'US'),
                    'is_active': account.get('ActiveFlag', True),
                    'opening_balance': random.uniform(10000, 100000),  # Fake balance
                    'closing_balance': 0.0,  # Will be calculated
                    'transactions': []  # Will be populated with fake transactions
                }
                
                processed_accounts.append(processed_account)
            
            return processed_accounts
            
        except Exception as e:
            print(f"Error processing bank accounts: {str(e)}")
            return []
    
    def generate_realistic_transactions(self, account: Dict[str, Any], transaction_count: int) -> List[Dict[str, Any]]:
        """
        Generate realistic transactions for a real bank account
        
        Args:
            account: Real bank account dictionary
            transaction_count: Number of transactions to generate
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        current_balance = account['opening_balance']
        
        # Transaction types based on real bank account
        transaction_types = ['CREDIT', 'DEBIT']
        
        # Realistic descriptions based on account type
        descriptions = [
            'ACH Credit', 'Wire Transfer', 'Check Payment', 'Direct Deposit',
            'ATM Withdrawal', 'Online Payment', 'Service Charge', 'Interest Earned',
            'Fee Charged', 'Electronic Transfer', 'Cash Deposit', 'Check Deposit'
        ]
        
        # Generate transactions
        for i in range(transaction_count):
            # Random date within last 30 days
            transaction_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Realistic amount based on account type
            if account['account_name'].lower().find('payroll') != -1:
                # Payroll account - larger amounts
                amount = random.uniform(1000, 50000)
            elif account['account_name'].lower().find('operating') != -1:
                # Operating account - medium amounts
                amount = random.uniform(500, 25000)
            else:
                # General account - standard amounts
                amount = random.uniform(
                    self.config['transactions']['bank_statement']['min_amount'],
                    self.config['transactions']['bank_statement']['max_amount']
                )
            
            # Transaction type (more credits for certain account types)
            if account['account_name'].lower().find('receivable') != -1:
                transaction_type = 'CREDIT' if random.random() > 0.3 else 'DEBIT'
            elif account['account_name'].lower().find('payable') != -1:
                transaction_type = 'DEBIT' if random.random() > 0.3 else 'CREDIT'
            else:
                transaction_type = random.choice(transaction_types)
            
            # Adjust balance
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
                'running_balance': round(current_balance, 2),
                'account_id': account['account_id'],
                'account_name': account['account_name']
            }
            
            transactions.append(transaction)
        
        # Update closing balance
        account['closing_balance'] = round(current_balance, 2)
        
        return transactions
    
    def create_bai2_with_real_accounts(self, real_accounts: List[Dict[str, Any]], transactions_per_account: int = None) -> str:
        """
        Create BAI2 file using real bank account information
        
        Args:
            real_accounts: List of real bank accounts from Oracle Fusion
            transactions_per_account: Number of transactions per account
            
        Returns:
            Path to generated BAI2 file
        """
        if transactions_per_account is None:
            transactions_per_account = self.config['transactions']['bank_statement']['default_count']
        
        # Generate transactions for each real account
        for account in real_accounts:
            account['transactions'] = self.generate_realistic_transactions(account, transactions_per_account)
        
        # Generate BAI2 file using the existing generator
        from .bai2_generator import BAI2Generator
        bai2_gen = BAI2Generator()
        
        # Convert real accounts to BAI2 format
        bai2_accounts = []
        for account in real_accounts:
            bai2_account = {
                'account_number': account['account_number'],
                'account_name': account['account_name'],
                'currency': account['currency'],
                'opening_balance': account['opening_balance'],
                'closing_balance': account['closing_balance'],
                'transactions': account['transactions']
            }
            bai2_accounts.append(bai2_account)
        
        # Generate BAI2 file
        output_file = bai2_gen.generate_bai2_file(bai2_accounts)
        
        return output_file
    
    def create_external_transactions_for_real_accounts(self, real_accounts: List[Dict[str, Any]], transaction_count: int = None) -> List[Dict[str, Any]]:
        """
        Create external cash transactions for real bank accounts
        
        Args:
            real_accounts: List of real bank accounts
            transaction_count: Number of transactions to generate
            
        Returns:
            List of external cash transactions
        """
        if transaction_count is None:
            transaction_count = self.config['transactions']['bank_statement']['default_count']
        
        external_transactions = []
        transaction_types = ['RECEIPT', 'PAYMENT', 'TRANSFER']
        
        for i in range(transaction_count):
            # Select a random real account
            account = random.choice(real_accounts)
            
            # Random date within last 30 days
            transaction_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Realistic amount
            amount = random.uniform(
                self.config['transactions']['bank_statement']['min_amount'],
                self.config['transactions']['bank_statement']['max_amount']
            )
            
            transaction = {
                'transactionType': random.choice(transaction_types),
                'transactionDate': transaction_date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'currency': account['currency'],
                'reference': f"EXT{random.randint(100000, 999999)}",
                'description': f"External transaction for {account['account_name']}",
                'bankAccountId': account['account_id'],
                'bankAccountName': account['account_name'],
                'status': 'PENDING'
            }
            
            external_transactions.append(transaction)
        
        return external_transactions 