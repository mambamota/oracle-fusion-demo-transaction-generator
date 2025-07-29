"""
Transaction Generators
Generate AP invoices, AR invoices, GL journals, and external cash transactions
"""

import random
import datetime
from typing import List, Dict, Any
from faker import Faker
import yaml

class TransactionGenerators:
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize transaction generators
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.fake = Faker()
        
    def generate_external_cash_transactions(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Generate external cash management transactions for auto-reconciliation
        
        Args:
            count: Number of transactions to generate
            
        Returns:
            List of external cash transaction dictionaries
        """
        if count is None:
            count = self.config['transactions']['bank_statement']['default_count']
        
        transactions = []
        transaction_types = ['RECEIPT', 'PAYMENT', 'TRANSFER']
        
        for i in range(count):
            # Random date within last 30 days
            transaction_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Random amount
            amount = random.uniform(
                self.config['transactions']['bank_statement']['min_amount'],
                self.config['transactions']['bank_statement']['max_amount']
            )
            
            transaction = {
                'transactionType': random.choice(transaction_types),
                'transactionDate': transaction_date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'currency': 'USD',
                'reference': f"EXT{random.randint(100000, 999999)}",
                'description': f"External transaction {i+1}",
                'bankAccountId': f"ACC{random.randint(1000, 9999)}",
                'status': 'PENDING'
            }
            
            transactions.append(transaction)
        
        return transactions
    
    def generate_ap_invoices(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Generate AP (Accounts Payable) invoices
        
        Args:
            count: Number of invoices to generate
            
        Returns:
            List of AP invoice dictionaries
        """
        if count is None:
            count = self.config['transactions']['ap_invoices']['default_count']
        
        invoices = []
        suppliers = [
            'ABC Supplies Inc.', 'XYZ Corporation', 'Global Services Ltd.',
            'Tech Solutions Co.', 'Office Equipment Corp.', 'Marketing Partners LLC'
        ]
        
        for i in range(count):
            # Random date within last 30 days
            invoice_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Random amount
            amount = random.uniform(
                self.config['transactions']['ap_invoices']['min_amount'],
                self.config['transactions']['ap_invoices']['max_amount']
            )
            
            # Generate line items
            line_items = []
            num_items = random.randint(1, 5)
            remaining_amount = amount
            
            for j in range(num_items):
                if j == num_items - 1:  # Last item gets remaining amount
                    item_amount = remaining_amount
                else:
                    item_amount = round(random.uniform(10, remaining_amount / (num_items - j)), 2)
                    remaining_amount -= item_amount
                
                line_item = {
                    'lineNumber': j + 1,
                    'description': f"Item {j+1}",
                    'quantity': random.randint(1, 10),
                    'unitPrice': round(item_amount / random.randint(1, 10), 2),
                    'amount': round(item_amount, 2),
                    'accountId': f"AP{random.randint(1000, 9999)}"
                }
                line_items.append(line_item)
            
            invoice = {
                'invoiceNumber': f"INV-{random.randint(10000, 99999)}",
                'supplierName': random.choice(suppliers),
                'invoiceDate': invoice_date.strftime('%Y-%m-%d'),
                'dueDate': (invoice_date + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'currency': 'USD',
                'status': 'PENDING',
                'lineItems': line_items,
                'description': f"AP Invoice {i+1}",
                'paymentTerms': 'NET30'
            }
            
            invoices.append(invoice)
        
        return invoices
    
    def generate_ar_invoices(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Generate AR (Accounts Receivable) invoices
        
        Args:
            count: Number of invoices to generate
            
        Returns:
            List of AR invoice dictionaries
        """
        if count is None:
            count = self.config['transactions']['ar_invoices']['default_count']
        
        invoices = []
        customers = [
            'Acme Corporation', 'Beta Industries', 'Gamma Solutions',
            'Delta Technologies', 'Epsilon Services', 'Zeta Enterprises'
        ]
        
        for i in range(count):
            # Random date within last 30 days
            invoice_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Random amount
            amount = random.uniform(
                self.config['transactions']['ar_invoices']['min_amount'],
                self.config['transactions']['ar_invoices']['max_amount']
            )
            
            # Generate line items
            line_items = []
            num_items = random.randint(1, 5)
            remaining_amount = amount
            
            for j in range(num_items):
                if j == num_items - 1:  # Last item gets remaining amount
                    item_amount = remaining_amount
                else:
                    item_amount = round(random.uniform(10, remaining_amount / (num_items - j)), 2)
                    remaining_amount -= item_amount
                
                line_item = {
                    'lineNumber': j + 1,
                    'description': f"Service {j+1}",
                    'quantity': random.randint(1, 10),
                    'unitPrice': round(item_amount / random.randint(1, 10), 2),
                    'amount': round(item_amount, 2),
                    'accountId': f"AR{random.randint(1000, 9999)}"
                }
                line_items.append(line_item)
            
            invoice = {
                'invoiceNumber': f"AR-INV-{random.randint(10000, 99999)}",
                'customerName': random.choice(customers),
                'invoiceDate': invoice_date.strftime('%Y-%m-%d'),
                'dueDate': (invoice_date + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'currency': 'USD',
                'status': 'PENDING',
                'lineItems': line_items,
                'description': f"AR Invoice {i+1}",
                'paymentTerms': 'NET30'
            }
            
            invoices.append(invoice)
        
        return invoices
    
    def generate_gl_journals(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Generate GL (General Ledger) journal entries
        
        Args:
            count: Number of journal entries to generate
            
        Returns:
            List of GL journal dictionaries
        """
        if count is None:
            count = self.config['transactions']['gl_journals']['default_count']
        
        journals = []
        account_combinations = [
            ('Cash', 'Accounts Receivable'),
            ('Accounts Payable', 'Cash'),
            ('Revenue', 'Accounts Receivable'),
            ('Expenses', 'Cash'),
            ('Prepaid Expenses', 'Cash'),
            ('Depreciation', 'Accumulated Depreciation')
        ]
        
        for i in range(count):
            # Random date within last 30 days
            journal_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Random amount
            amount = random.uniform(
                self.config['transactions']['gl_journals']['min_amount'],
                self.config['transactions']['gl_journals']['max_amount']
            )
            
            # Select random account combination
            debit_account, credit_account = random.choice(account_combinations)
            
            journal = {
                'journalNumber': f"JE-{random.randint(10000, 99999)}",
                'journalDate': journal_date.strftime('%Y-%m-%d'),
                'description': f"GL Journal Entry {i+1}",
                'status': 'PENDING',
                'currency': 'USD',
                'lines': [
                    {
                        'lineNumber': 1,
                        'accountId': f"GL{random.randint(1000, 9999)}",
                        'accountName': debit_account,
                        'debitAmount': round(amount, 2),
                        'creditAmount': 0.0,
                        'description': f"Debit to {debit_account}"
                    },
                    {
                        'lineNumber': 2,
                        'accountId': f"GL{random.randint(1000, 9999)}",
                        'accountName': credit_account,
                        'debitAmount': 0.0,
                        'creditAmount': round(amount, 2),
                        'description': f"Credit to {credit_account}"
                    }
                ],
                'totalDebits': round(amount, 2),
                'totalCredits': round(amount, 2)
            }
            
            journals.append(journal)
        
        return journals
    
    def generate_ar_receipts(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Generate AR (Accounts Receivable) receipts
        
        Args:
            count: Number of receipts to generate
            
        Returns:
            List of AR receipt dictionaries
        """
        if count is None:
            count = self.config['transactions']['ar_invoices']['default_count']
        
        receipts = []
        payment_methods = ['CHECK', 'WIRE', 'ACH', 'CASH']
        
        for i in range(count):
            # Random date within last 30 days
            receipt_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, self.config['transactions']['bank_statement']['date_range_days'])
            )
            
            # Random amount
            amount = random.uniform(
                self.config['transactions']['ar_invoices']['min_amount'],
                self.config['transactions']['ar_invoices']['max_amount']
            )
            
            receipt = {
                'receiptNumber': f"RCPT-{random.randint(10000, 99999)}",
                'customerName': self.fake.company(),
                'receiptDate': receipt_date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'currency': 'USD',
                'paymentMethod': random.choice(payment_methods),
                'status': 'PENDING',
                'description': f"AR Receipt {i+1}",
                'reference': f"REF{random.randint(100000, 999999)}"
            }
            
            receipts.append(receipt)
        
        return receipts 