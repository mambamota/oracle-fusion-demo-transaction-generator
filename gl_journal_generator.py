import random
import datetime
from typing import List, Dict, Any
from faker import Faker

class GLJournalGenerator:
    def __init__(self):
        self.fake = Faker()
        self.journal_types = ['STANDARD', 'ADJUSTMENT', 'RECLASSIFICATION', 'REVERSAL']
        self.business_units = ['US1 Business Unit', 'UK Business Unit', 'CA Business Unit']
        self.currencies = ['USD', 'CAD', 'EUR', 'GBP']
        self.ledgers = ['US Primary Ledger', 'UK Primary Ledger', 'CA Primary Ledger']
        self.account_types = ['ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE']
        
        # Common GL accounts for different scenarios
        self.gl_accounts = {
            'ASSET': ['1000', '1100', '1200', '1300', '1400', '1500'],  # Cash, AR, Inventory, etc.
            'LIABILITY': ['2000', '2100', '2200', '2300', '2400'],       # AP, Accruals, etc.
            'EQUITY': ['3000', '3100', '3200', '3300'],                  # Common Stock, Retained Earnings
            'REVENUE': ['4000', '4100', '4200', '4300', '4400'],         # Sales, Service Revenue
            'EXPENSE': ['5000', '5100', '5200', '5300', '5400', '5500']  # COGS, Operating Expenses
        }
        
        self.journal_sources = ['MANUAL', 'AP', 'AR', 'CASH', 'INVENTORY', 'PAYROLL']
        self.journal_categories = ['GENERAL', 'ADJUSTMENT', 'RECLASSIFICATION', 'REVERSAL']
        self.period_names = ['JAN-2025', 'FEB-2025', 'MAR-2025', 'APR-2025', 'MAY-2025', 'JUN-2025']

    def generate_gl_journals(self, accounts: List[Dict[str, Any]], 
                            journals_per_account: int = 2,
                            lines_per_journal: int = 3,
                            date_range_days: int = 30) -> List[Dict[str, Any]]:
        """Generate GL journal entries"""
        journals = []
        
        for account in accounts:
            for journal_num in range(journals_per_account):
                # Generate journal header
                journal_date = datetime.datetime.now() - datetime.timedelta(
                    days=random.randint(1, date_range_days)
                )
                
                journal_header = {
                    'JournalId': f"GL-{account['account_name'][:3].upper()}-{journal_num+1:03d}",
                    'JournalName': f"Demo GL Journal {journal_num+1} for {account['account_name']}",
                    'JournalDate': journal_date.strftime('%Y/%m/%d'),
                    'JournalType': random.choice(self.journal_types),
                    'BusinessUnit': random.choice(self.business_units),
                    'Ledger': random.choice(self.ledgers),
                    'Currency': account['currency'],
                    'JournalSource': random.choice(self.journal_sources),
                    'JournalCategory': random.choice(self.journal_categories),
                    'PeriodName': random.choice(self.period_names),
                    'Status': 'DRAFT',
                    'Description': f"Demo GL journal entry for {account['account_name']}",
                    'TotalDebit': 0.0,
                    'TotalCredit': 0.0
                }
                
                # Generate journal lines
                journal_lines = []
                total_debit = 0.0
                total_credit = 0.0
                
                for line_num in range(lines_per_journal):
                    # Ensure balanced journal (debits = credits)
                    if line_num == lines_per_journal - 1:
                        # Last line balances the journal
                        if total_debit > total_credit:
                            amount = total_debit - total_credit
                            line_type = 'CREDIT'
                            total_credit += amount
                        else:
                            amount = total_credit - total_debit
                            line_type = 'DEBIT'
                            total_debit += amount
                    else:
                        # Random line
                        amount = round(random.uniform(1000, 10000), 2)
                        line_type = random.choice(['DEBIT', 'CREDIT'])
                        if line_type == 'DEBIT':
                            total_debit += amount
                        else:
                            total_credit += amount
                    
                    # Select account type and GL account
                    account_type = random.choice(self.account_types)
                    gl_account = random.choice(self.gl_accounts[account_type])
                    
                    journal_line = {
                        'LineNumber': line_num + 1,
                        'AccountType': account_type,
                        'GLAccount': gl_account,
                        'Description': f"Demo GL line {line_num + 1}",
                        'DebitAmount': amount if line_type == 'DEBIT' else 0.0,
                        'CreditAmount': amount if line_type == 'CREDIT' else 0.0,
                        'LineType': line_type,
                        'Currency': account['currency'],
                        'BusinessUnit': journal_header['BusinessUnit'],
                        'Ledger': journal_header['Ledger'],
                        'PeriodName': journal_header['PeriodName'],
                        'Status': 'DRAFT'
                    }
                    journal_lines.append(journal_line)
                
                # Update header totals
                journal_header['TotalDebit'] = total_debit
                journal_header['TotalCredit'] = total_credit
                
                journals.append({
                    'header': journal_header,
                    'lines': journal_lines
                })
        
        return journals

    def generate_csv_content(self, journals: List[Dict[str, Any]]) -> str:
        """Generate CSV content for GL journal import"""
        csv_lines = []
        
        # Header
        header = [
            'JournalId', 'JournalName', 'JournalDate', 'JournalType', 'BusinessUnit',
            'Ledger', 'Currency', 'JournalSource', 'JournalCategory', 'PeriodName',
            'Status', 'Description', 'TotalDebit', 'TotalCredit',
            'LineNumber', 'AccountType', 'GLAccount', 'LineDescription', 
            'DebitAmount', 'CreditAmount', 'LineType', 'LineStatus'
        ]
        csv_lines.append(','.join(header))
        
        # Data rows
        for journal in journals:
            header = journal['header']
            for line in journal['lines']:
                row = [
                    header['JournalId'],
                    header['JournalName'],
                    header['JournalDate'],
                    header['JournalType'],
                    header['BusinessUnit'],
                    header['Ledger'],
                    header['Currency'],
                    header['JournalSource'],
                    header['JournalCategory'],
                    header['PeriodName'],
                    header['Status'],
                    header['Description'],
                    str(header['TotalDebit']),
                    str(header['TotalCredit']),
                    str(line['LineNumber']),
                    line['AccountType'],
                    line['GLAccount'],
                    line['Description'],
                    str(line['DebitAmount']),
                    str(line['CreditAmount']),
                    line['LineType'],
                    line['Status']
                ]
                csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)

    def generate_oracle_fusion_format(self, journals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate Oracle Fusion API format for GL journals"""
        fusion_journals = []
        
        for journal in journals:
            header = journal['header']
            fusion_journal = {
                'journalId': header['JournalId'],
                'journalName': header['JournalName'],
                'journalDate': header['JournalDate'],
                'journalType': header['JournalType'],
                'businessUnit': header['BusinessUnit'],
                'ledger': header['Ledger'],
                'currency': header['Currency'],
                'journalSource': header['JournalSource'],
                'journalCategory': header['JournalCategory'],
                'periodName': header['PeriodName'],
                'status': header['Status'],
                'description': header['Description'],
                'totalDebit': header['TotalDebit'],
                'totalCredit': header['TotalCredit'],
                'lines': []
            }
            
            for line in journal['lines']:
                fusion_line = {
                    'lineNumber': line['LineNumber'],
                    'accountType': line['AccountType'],
                    'glAccount': line['GLAccount'],
                    'description': line['Description'],
                    'debitAmount': line['DebitAmount'],
                    'creditAmount': line['CreditAmount'],
                    'lineType': line['LineType'],
                    'currency': line['Currency'],
                    'businessUnit': line['BusinessUnit'],
                    'ledger': line['Ledger'],
                    'periodName': line['PeriodName'],
                    'status': line['Status']
                }
                fusion_journal['lines'].append(fusion_line)
            
            fusion_journals.append(fusion_journal)
        
        return fusion_journals

    def generate_properties_content(self, journals: List[Dict[str, Any]]) -> str:
        """Generate properties file content for GL journal import"""
        properties_lines = []
        
        # Add header comment
        properties_lines.append("# GL Journal Import Properties")
        properties_lines.append("# Generated for Oracle Fusion Demo")
        properties_lines.append("")
        
        # Add journal properties
        for journal in journals:
            header = journal['header']
            properties_lines.append(f"# Journal: {header['JournalId']}")
            properties_lines.append(f"journal.id={header['JournalId']}")
            properties_lines.append(f"journal.name={header['JournalName']}")
            properties_lines.append(f"journal.type={header['JournalType']}")
            properties_lines.append(f"journal.businessUnit={header['BusinessUnit']}")
            properties_lines.append(f"journal.ledger={header['Ledger']}")
            properties_lines.append(f"journal.currency={header['Currency']}")
            properties_lines.append(f"journal.source={header['JournalSource']}")
            properties_lines.append(f"journal.category={header['JournalCategory']}")
            properties_lines.append(f"journal.period={header['PeriodName']}")
            properties_lines.append(f"journal.status={header['Status']}")
            properties_lines.append("")
        
        return '\n'.join(properties_lines) 