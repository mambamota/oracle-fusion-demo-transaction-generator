import random
import datetime
from typing import List, Dict, Any
from faker import Faker

class ARInvoiceGenerator:
    def __init__(self):
        self.fake = Faker()
        self.invoice_types = ['STANDARD', 'CREDIT_MEMO', 'DEBIT_MEMO', 'ADVANCE']
        self.business_units = ['US1 Business Unit', 'UK Business Unit', 'CA Business Unit']
        self.currencies = ['USD', 'CAD', 'EUR', 'GBP']
        self.revenue_categories = [
            'Product Sales', 'Service Revenue', 'Consulting Fees',
            'Software Licenses', 'Maintenance & Support', 'Training Services',
            'Professional Services', 'Subscription Revenue', 'Implementation Services',
            'Custom Development'
        ]
        self.payment_terms = ['NET30', 'NET60', 'NET90', 'DUE_ON_RECEIPT', 'NET15']
        
    def generate_ar_invoices(self, accounts: List[Dict[str, Any]], 
                           invoices_per_account: int = 3,
                           lines_per_invoice: int = 2,
                           date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Generate AR invoices for Oracle Fusion"""
        
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
                    'InvoiceId': f"AR-{account_name[:3].upper()}-{i+1:03d}",
                    'InvoiceNumber': f"AR{i+1:06d}",
                    'InvoiceDate': invoice_date.strftime('%Y/%m/%d'),
                    'DueDate': due_date.strftime('%Y/%m/%d'),
                    'InvoiceType': random.choice(self.invoice_types),
                    'BusinessUnit': random.choice(self.business_units),
                    'Currency': currency,
                    'CustomerName': self.fake.company(),
                    'CustomerNumber': f"CUST{random.randint(1000, 9999)}",
                    'InvoiceAmount': 0.0,  # Will be calculated from lines
                    'Status': 'PENDING_APPROVAL',
                    'PaymentTerms': random.choice(self.payment_terms),
                    'Description': f"Demo AR Invoice {i+1} for {account_name}"
                }
                
                # Generate invoice lines
                invoice_lines = []
                total_amount = 0.0
                
                for j in range(lines_per_invoice):
                    line_amount = random.uniform(500, 10000)
                    total_amount += line_amount
                    
                    line = {
                        'LineNumber': j + 1,
                        'LineType': 'ITEM',
                        'Amount': round(line_amount, 2),
                        'Quantity': random.randint(1, 20),
                        'UnitPrice': round(line_amount / random.randint(1, 20), 2),
                        'Description': random.choice(self.revenue_categories),
                        'RevenueCategory': random.choice(self.revenue_categories),
                        'GLAccount': f"GL{random.randint(2000, 9999)}",  # Revenue accounts
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
    
    def generate_receipts(self, invoices: List[Dict[str, Any]], 
                         receipt_percentage: float = 0.7) -> List[Dict[str, Any]]:
        """Generate receipts for AR invoices"""
        
        receipts = []
        
        for invoice in invoices:
            # 70% of invoices get receipts by default
            if random.random() <= receipt_percentage:
                header = invoice['header']
                
                # Generate receipt date (after invoice date, before due date)
                invoice_date = datetime.datetime.strptime(header['InvoiceDate'], '%Y/%m/%d')
                due_date = datetime.datetime.strptime(header['DueDate'], '%Y/%m/%d')
                
                # Receipt date between invoice and due date
                days_between = (due_date - invoice_date).days
                receipt_days = random.randint(0, days_between)
                receipt_date = invoice_date + datetime.timedelta(days=receipt_days)
                
                receipt = {
                    'ReceiptId': f"RCPT-{header['InvoiceId']}",
                    'ReceiptNumber': f"RCPT{random.randint(1000, 9999)}",
                    'InvoiceId': header['InvoiceId'],
                    'InvoiceNumber': header['InvoiceNumber'],
                    'CustomerName': header['CustomerName'],
                    'CustomerNumber': header['CustomerNumber'],
                    'ReceiptDate': receipt_date.strftime('%Y/%m/%d'),
                    'Amount': header['InvoiceAmount'],
                    'Currency': header['Currency'],
                    'PaymentMethod': random.choice(['CHECK', 'WIRE', 'ACH', 'CREDIT_CARD']),
                    'Reference': f"PAY-{header['CustomerNumber']}-{random.randint(100, 999)}",
                    'Status': 'APPLIED',
                    'BusinessUnit': header['BusinessUnit']
                }
                
                receipts.append(receipt)
        
        return receipts
    
    def generate_csv_content(self, invoices: List[Dict[str, Any]]) -> str:
        """Generate CSV content for AR invoice lines interface"""
        if not invoices:
            return ""
        
        # CSV header for AR invoices
        csv_lines = [
            'InvoiceId,LineNumber,LineType,Amount,Quantity,UnitPrice,Description,RevenueCategory,GLAccount,TaxCode,LineStatus,InvoiceDate,DueDate,InvoiceType,BusinessUnit,Currency,CustomerName,CustomerNumber,InvoiceAmount,Status,PaymentTerms'
        ]
        
        # CSV data rows
        for invoice in invoices:
            header = invoice['header']
            for line in invoice['lines']:
                csv_line = f"{header['InvoiceId']},{line['LineNumber']},{line['LineType']},{line['Amount']},{line['Quantity']},{line['UnitPrice']},{line['Description']},{line['RevenueCategory']},{line['GLAccount']},{line['TaxCode']},{line['LineStatus']},{header['InvoiceDate']},{header['DueDate']},{header['InvoiceType']},{header['BusinessUnit']},{header['Currency']},{header['CustomerName']},{header['CustomerNumber']},{header['InvoiceAmount']},{header['Status']},{header['PaymentTerms']}"
                csv_lines.append(csv_line)
        
        return '\n'.join(csv_lines)
    
    def generate_receipts_csv_content(self, receipts: List[Dict[str, Any]]) -> str:
        """Generate CSV content for AR receipts"""
        if not receipts:
            return ""
        
        # CSV header for receipts
        csv_lines = [
            'ReceiptId,ReceiptNumber,InvoiceId,InvoiceNumber,CustomerName,CustomerNumber,ReceiptDate,Amount,Currency,PaymentMethod,Reference,Status,BusinessUnit'
        ]
        
        # CSV data rows
        for receipt in receipts:
            csv_line = f"{receipt['ReceiptId']},{receipt['ReceiptNumber']},{receipt['InvoiceId']},{receipt['InvoiceNumber']},{receipt['CustomerName']},{receipt['CustomerNumber']},{receipt['ReceiptDate']},{receipt['Amount']},{receipt['Currency']},{receipt['PaymentMethod']},{receipt['Reference']},{receipt['Status']},{receipt['BusinessUnit']}"
            csv_lines.append(csv_line)
        
        return '\n'.join(csv_lines)
    
    def generate_oracle_fusion_format(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate Oracle Fusion API format for posting AR invoices"""
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
                'customerName': header['CustomerName'],
                'customerNumber': header['CustomerNumber'],
                'invoiceAmount': header['InvoiceAmount'],
                'status': header['Status'],
                'paymentTerms': header['PaymentTerms'],
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
                    'revenueCategory': line['RevenueCategory'],
                    'glAccount': line['GLAccount'],
                    'taxCode': line['TaxCode'],
                    'lineStatus': line['LineStatus']
                }
                fusion_invoice['lines'].append(fusion_line)
            
            fusion_invoices.append(fusion_invoice)
        
        return fusion_invoices 