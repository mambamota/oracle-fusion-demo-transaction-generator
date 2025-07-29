"""
Excel Exporter
Export generated transaction data to Excel files for review and analysis
"""

import pandas as pd
from typing import List, Dict, Any
import yaml
from datetime import datetime

class ExcelExporter:
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize Excel exporter
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def export_bank_statement_data(self, accounts: List[Dict[str, Any]], output_file: str = None) -> str:
        """
        Export bank statement data to Excel
        
        Args:
            accounts: List of bank accounts with transactions
            output_file: Output file path (optional)
            
        Returns:
            Path to generated Excel file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"bank_statement_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Create summary sheet
            summary_data = []
            for account in accounts:
                summary_data.append({
                    'Account Number': account['account_number'],
                    'Account Name': account['account_name'],
                    'Currency': account['currency'],
                    'Opening Balance': account['opening_balance'],
                    'Closing Balance': account['closing_balance'],
                    'Transaction Count': len(account.get('transactions', [])),
                    'Total Credits': sum(t['amount'] for t in account.get('transactions', []) if t['type'] == 'CREDIT'),
                    'Total Debits': sum(t['amount'] for t in account.get('transactions', []) if t['type'] == 'DEBIT')
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create transaction details sheet
            all_transactions = []
            for account in accounts:
                for transaction in account.get('transactions', []):
                    all_transactions.append({
                        'Account Number': account['account_number'],
                        'Account Name': account['account_name'],
                        'Date': transaction['date'],
                        'Type': transaction['type'],
                        'Amount': transaction['amount'],
                        'Reference': transaction['reference'],
                        'Description': transaction['description'],
                        'Running Balance': transaction['running_balance']
                    })
            
            if all_transactions:
                transactions_df = pd.DataFrame(all_transactions)
                transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
        
        return output_file
    
    def export_transaction_data(self, data: Dict[str, List[Dict[str, Any]]], output_file: str = None) -> str:
        """
        Export all transaction data to Excel with multiple sheets
        
        Args:
            data: Dictionary containing different transaction types
            output_file: Output file path (optional)
            
        Returns:
            Path to generated Excel file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"demo_transactions_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Export each transaction type to separate sheets
            for transaction_type, transactions in data.items():
                if transactions:
                    df = pd.DataFrame(transactions)
                    
                    # Clean up column names for Excel
                    df.columns = [col.replace('_', ' ').title() for col in df.columns]
                    
                    # Write to Excel with proper sheet name
                    sheet_name = transaction_type.replace('_', ' ').title()
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Create summary sheet
            summary_data = []
            for transaction_type, transactions in data.items():
                if transactions:
                    summary_data.append({
                        'Transaction Type': transaction_type.replace('_', ' ').title(),
                        'Count': len(transactions),
                        'Total Amount': sum(t.get('amount', 0) for t in transactions),
                        'Average Amount': sum(t.get('amount', 0) for t in transactions) / len(transactions) if transactions else 0
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return output_file
    
    def export_ap_invoices(self, invoices: List[Dict[str, Any]], output_file: str = None) -> str:
        """
        Export AP invoices to Excel
        
        Args:
            invoices: List of AP invoices
            output_file: Output file path (optional)
            
        Returns:
            Path to generated Excel file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"ap_invoices_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Main invoice data
            invoice_data = []
            for invoice in invoices:
                invoice_data.append({
                    'Invoice Number': invoice['invoiceNumber'],
                    'Supplier Name': invoice['supplierName'],
                    'Invoice Date': invoice['invoiceDate'],
                    'Due Date': invoice['dueDate'],
                    'Amount': invoice['amount'],
                    'Currency': invoice['currency'],
                    'Status': invoice['status'],
                    'Description': invoice['description'],
                    'Payment Terms': invoice['paymentTerms']
                })
            
            if invoice_data:
                invoice_df = pd.DataFrame(invoice_data)
                invoice_df.to_excel(writer, sheet_name='Invoices', index=False)
            
            # Line items data
            line_items_data = []
            for invoice in invoices:
                for line_item in invoice.get('lineItems', []):
                    line_items_data.append({
                        'Invoice Number': invoice['invoiceNumber'],
                        'Line Number': line_item['lineNumber'],
                        'Description': line_item['description'],
                        'Quantity': line_item['quantity'],
                        'Unit Price': line_item['unitPrice'],
                        'Amount': line_item['amount'],
                        'Account ID': line_item['accountId']
                    })
            
            if line_items_data:
                line_items_df = pd.DataFrame(line_items_data)
                line_items_df.to_excel(writer, sheet_name='Line Items', index=False)
        
        return output_file
    
    def export_ar_invoices(self, invoices: List[Dict[str, Any]], output_file: str = None) -> str:
        """
        Export AR invoices to Excel
        
        Args:
            invoices: List of AR invoices
            output_file: Output file path (optional)
            
        Returns:
            Path to generated Excel file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"ar_invoices_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Main invoice data
            invoice_data = []
            for invoice in invoices:
                invoice_data.append({
                    'Invoice Number': invoice['invoiceNumber'],
                    'Customer Name': invoice['customerName'],
                    'Invoice Date': invoice['invoiceDate'],
                    'Due Date': invoice['dueDate'],
                    'Amount': invoice['amount'],
                    'Currency': invoice['currency'],
                    'Status': invoice['status'],
                    'Description': invoice['description'],
                    'Payment Terms': invoice['paymentTerms']
                })
            
            if invoice_data:
                invoice_df = pd.DataFrame(invoice_data)
                invoice_df.to_excel(writer, sheet_name='Invoices', index=False)
            
            # Line items data
            line_items_data = []
            for invoice in invoices:
                for line_item in invoice.get('lineItems', []):
                    line_items_data.append({
                        'Invoice Number': invoice['invoiceNumber'],
                        'Line Number': line_item['lineNumber'],
                        'Description': line_item['description'],
                        'Quantity': line_item['quantity'],
                        'Unit Price': line_item['unitPrice'],
                        'Amount': line_item['amount'],
                        'Account ID': line_item['accountId']
                    })
            
            if line_items_data:
                line_items_df = pd.DataFrame(line_items_data)
                line_items_df.to_excel(writer, sheet_name='Line Items', index=False)
        
        return output_file
    
    def export_gl_journals(self, journals: List[Dict[str, Any]], output_file: str = None) -> str:
        """
        Export GL journals to Excel
        
        Args:
            journals: List of GL journals
            output_file: Output file path (optional)
            
        Returns:
            Path to generated Excel file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"gl_journals_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Main journal data
            journal_data = []
            for journal in journals:
                journal_data.append({
                    'Journal Number': journal['journalNumber'],
                    'Journal Date': journal['journalDate'],
                    'Description': journal['description'],
                    'Status': journal['status'],
                    'Currency': journal['currency'],
                    'Total Debits': journal['totalDebits'],
                    'Total Credits': journal['totalCredits']
                })
            
            if journal_data:
                journal_df = pd.DataFrame(journal_data)
                journal_df.to_excel(writer, sheet_name='Journals', index=False)
            
            # Journal lines data
            lines_data = []
            for journal in journals:
                for line in journal.get('lines', []):
                    lines_data.append({
                        'Journal Number': journal['journalNumber'],
                        'Line Number': line['lineNumber'],
                        'Account Name': line['accountName'],
                        'Account ID': line['accountId'],
                        'Debit Amount': line['debitAmount'],
                        'Credit Amount': line['creditAmount'],
                        'Description': line['description']
                    })
            
            if lines_data:
                lines_df = pd.DataFrame(lines_data)
                lines_df.to_excel(writer, sheet_name='Journal Lines', index=False)
        
        return output_file 