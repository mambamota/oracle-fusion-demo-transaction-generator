import random
import datetime
from typing import List, Dict, Any
from faker import Faker

class APInvoiceGenerator:
    def __init__(self):
        self.fake = Faker()
        self.invoice_types = ['STANDARD', 'PREPAYMENT', 'EXPENSE_REPORT']
        self.business_units = ['US1 Business Unit', 'UK Business Unit', 'CA Business Unit']
        self.currencies = ['USD', 'CAD', 'EUR', 'GBP']
        self.expense_categories = [
            'Equipment Expense (Full)', 'Office Supplies', 'Travel & Entertainment',
            'Professional Services', 'Marketing Expenses', 'IT Services',
            'Utilities', 'Rent', 'Insurance', 'Maintenance'
        ]
        
    def generate_ap_invoices(self, accounts: List[Dict[str, Any]], 
                           invoices_per_account: int = 3,
                           lines_per_invoice: int = 2,
                           date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Generate AP invoices for Oracle Fusion"""
        
        invoices = []
        base_date = datetime.datetime.now()
        
        for account in accounts:
            account_name = account.get('account_name', 'Unknown Account')
            currency = account.get('currency', 'USD')
            
            for i in range(invoices_per_account):
                # Generate invoice header
                invoice_date = base_date - datetime.timedelta(days=random.randint(0, date_range_days))
                due_date = invoice_date + datetime.timedelta(days=random.randint(15, 45))
                
                invoice_header = {
                    'InvoiceId': f"INV-{account_name[:3].upper()}-{i+1:03d}",
                    'InvoiceNumber': f"INV{i+1:06d}",
                    'InvoiceDate': invoice_date.strftime('%Y/%m/%d'),
                    'DueDate': due_date.strftime('%Y/%m/%d'),
                    'InvoiceType': random.choice(self.invoice_types),
                    'BusinessUnit': random.choice(self.business_units),
                    'Currency': currency,
                    'SupplierName': self.fake.company(),
                    'SupplierNumber': f"SUP{random.randint(1000, 9999)}",
                    'InvoiceAmount': 0.0,  # Will be calculated from lines
                    'Status': 'PENDING_APPROVAL',
                    'Description': f"Demo AP Invoice {i+1} for {account_name}"
                }
                
                # Generate invoice lines
                invoice_lines = []
                total_amount = 0.0
                
                for j in range(lines_per_invoice):
                    line_amount = random.uniform(100, 5000)
                    total_amount += line_amount
                    
                    line = {
                        'LineNumber': j + 1,
                        'LineType': 'ITEM',
                        'Amount': round(line_amount, 2),
                        'Quantity': random.randint(1, 10),
                        'UnitPrice': round(line_amount / random.randint(1, 10), 2),
                        'Description': random.choice(self.expense_categories),
                        'ExpenseCategory': random.choice(self.expense_categories),
                        'GLAccount': f"GL{random.randint(1000, 9999)}",
                        'TaxCode': 'TAX_EXEMPT' if random.random() > 0.3 else 'STANDARD_TAX',
                        'LineStatus': 'PENDING'
                    }
                    invoice_lines.append(line)
                
                # Update invoice amount
                invoice_header['InvoiceAmount'] = round(total_amount, 2)
                
                # Combine header and lines
                invoice = {
                    'header': invoice_header,
                    'lines': invoice_lines
                }
                
                invoices.append(invoice)
        
        return invoices
    
    def generate_csv_content(self, invoices: List[Dict[str, Any]]) -> str:
        """Generate CSV content for AP invoice lines interface"""
        if not invoices:
            return ""
        
        # CSV header based on ApInvoiceLinesInterface.csv
        csv_lines = [
            'InvoiceId,LineNumber,LineType,Amount,Quantity,UnitPrice,Description,ExpenseCategory,GLAccount,TaxCode,LineStatus,InvoiceDate,DueDate,InvoiceType,BusinessUnit,Currency,SupplierName,SupplierNumber,InvoiceAmount,Status'
        ]
        
        # CSV data rows
        for invoice in invoices:
            header = invoice['header']
            for line in invoice['lines']:
                csv_line = f"{header['InvoiceId']},{line['LineNumber']},{line['LineType']},{line['Amount']},{line['Quantity']},{line['UnitPrice']},{line['Description']},{line['ExpenseCategory']},{line['GLAccount']},{line['TaxCode']},{line['LineStatus']},{header['InvoiceDate']},{header['DueDate']},{header['InvoiceType']},{header['BusinessUnit']},{header['Currency']},{header['SupplierName']},{header['SupplierNumber']},{header['InvoiceAmount']},{header['Status']}"
                csv_lines.append(csv_line)
        
        return '\n'.join(csv_lines)
    
    def generate_oracle_fusion_format(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate Oracle Fusion API format for posting AP invoices"""
        fusion_invoices = []
        
        for invoice in invoices:
            header = invoice['header']
            lines = invoice['lines']
            
            fusion_invoice = {
                'invoiceId': header['InvoiceId'],
                'invoiceNumber': header['InvoiceNumber'],
                'invoiceDate': header['InvoiceDate'],
                'dueDate': header['DueDate'],
                'invoiceType': header['InvoiceType'],
                'businessUnit': header['BusinessUnit'],
                'currency': header['Currency'],
                'supplierName': header['SupplierName'],
                'supplierNumber': header['SupplierNumber'],
                'invoiceAmount': header['InvoiceAmount'],
                'status': header['Status'],
                'description': header['Description'],
                'lines': []
            }
            
            # Add lines
            for line in lines:
                fusion_line = {
                    'lineNumber': line['LineNumber'],
                    'lineType': line['LineType'],
                    'amount': line['Amount'],
                    'quantity': line['Quantity'],
                    'unitPrice': line['UnitPrice'],
                    'description': line['Description'],
                    'expenseCategory': line['ExpenseCategory'],
                    'glAccount': line['GLAccount'],
                    'taxCode': line['TaxCode'],
                    'lineStatus': line['LineStatus']
                }
                fusion_invoice['lines'].append(fusion_line)
            
            fusion_invoices.append(fusion_invoice)
        
        return fusion_invoices
    
    def generate_properties_content(self, invoices: List[Dict[str, Any]]) -> str:
        """Generate properties file content for AP import"""
        if not invoices:
            return ""
        
        properties_lines = [
            "# AP Invoice Import Properties",
            "# Generated for Oracle Fusion AP Import",
            "",
            "# Import Settings",
            "import.source=External",
            "import.business.unit=US1 Business Unit",
            "import.ledger=US Primary Ledger",
            "import.currency=USD",
            "",
            "# Invoice Properties"
        ]
        
        for invoice in invoices:
            header = invoice['header']
            properties_lines.append(f"invoice.{header['InvoiceId']}.type={header['InvoiceType']}")
            properties_lines.append(f"invoice.{header['InvoiceId']}.supplier={header['SupplierNumber']}")
            properties_lines.append(f"invoice.{header['InvoiceId']}.amount={header['InvoiceAmount']}")
            properties_lines.append(f"invoice.{header['InvoiceId']}.currency={header['Currency']}")
            properties_lines.append("")
        
        return '\n'.join(properties_lines) 