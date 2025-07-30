import streamlit as st
import pandas as pd
import yaml
import os
import requests
from pathlib import Path

# Import BAI2 generator
try:
    from bai2_generator import BAI2Generator
    bai2_gen = BAI2Generator()
except ImportError:
    st.error("❌ BAI2 generator not found")
    bai2_gen = None

# Import External Cash generator
try:
    from external_cash_generator import ExternalCashGenerator
    external_cash_gen = ExternalCashGenerator()
except ImportError:
    st.error("❌ External cash generator not found")
    external_cash_gen = None

# Import AP Invoice generator
try:
    from ap_invoice_generator import APInvoiceGenerator
    ap_invoice_gen = APInvoiceGenerator()
except ImportError:
    st.error("❌ AP Invoice generator not found")
    ap_invoice_gen = None

# Import AR Invoice generator
try:
    from ar_invoice_generator import ARInvoiceGenerator
    ar_invoice_gen = ARInvoiceGenerator()
except ImportError:
    st.error("❌ AR Invoice generator not found")
    ar_invoice_gen = None

# Import GL Journal generator
try:
    from gl_journal_generator import GLJournalGenerator
    gl_journal_gen = GLJournalGenerator()
except ImportError:
    st.error("❌ GL Journal generator not found")
    gl_journal_gen = None

# Page configuration
st.set_page_config(
    page_title="Oracle Fusion Demo Transaction Generator",
    page_icon="🏦",
    layout="wide"
)

# Initialize session state
if 'real_accounts' not in st.session_state:
    st.session_state.real_accounts = []
if 'transactions_per_account' not in st.session_state:
    st.session_state.transactions_per_account = 10
if 'opening_balance' not in st.session_state:
    st.session_state.opening_balance = 50000.0
if 'target_closing_balance' not in st.session_state:
    st.session_state.target_closing_balance = 75000.0
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'password' not in st.session_state:
    st.session_state.password = ""
if 'base_url' not in st.session_state:
    st.session_state.base_url = "https://iabhzv-test.fa.ocs.oraclecloud.com"
if 'raw_api_response' not in st.session_state:
    st.session_state.raw_api_response = None
if 'external_transactions' not in st.session_state:
    st.session_state.external_transactions = []
if 'external_transactions_per_account' not in st.session_state:
    st.session_state.external_transactions_per_account = 5
if 'ap_invoices' not in st.session_state:
    st.session_state.ap_invoices = []
if 'ap_invoices_per_account' not in st.session_state:
    st.session_state.ap_invoices_per_account = 3
if 'ap_lines_per_invoice' not in st.session_state:
    st.session_state.ap_lines_per_invoice = 2
if 'ar_invoices' not in st.session_state:
    st.session_state.ar_invoices = []
if 'ar_receipts' not in st.session_state:
    st.session_state.ar_receipts = []
if 'ar_invoices_per_account' not in st.session_state:
    st.session_state.ar_invoices_per_account = 3
if 'ar_lines_per_invoice' not in st.session_state:
    st.session_state.ar_lines_per_invoice = 2
if 'gl_journals' not in st.session_state:
    st.session_state.gl_journals = []
if 'gl_journals_per_account' not in st.session_state:
    st.session_state.gl_journals_per_account = 2
if 'gl_lines_per_journal' not in st.session_state:
    st.session_state.gl_lines_per_journal = 3

st.title("🏦 Oracle Fusion Demo Transaction Generator")
st.markdown("Generate demo transactions for Oracle Fusion Financials testing")

# Load config
try:
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    else:
        config = {
            'oracle_fusion': {
                'base_url': st.session_state.base_url,
                'api_version': '11.13.18.05',
                'timeout': 30
            }
        }
    
    # Override base_url with session state if available
    if 'base_url' in st.session_state:
        config['oracle_fusion']['base_url'] = st.session_state.base_url
        
except Exception as e:
    st.error(f"Config error: {e}")
    config = {
        'oracle_fusion': {
            'base_url': st.session_state.base_url,
            'api_version': '11.13.18.05',
            'timeout': 30
        }
    }

# Simple Oracle client (inline to avoid import issues)
class SimpleOracleClient:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        # Use current config base URL (which may have been updated from session state)
        self.base_url = config['oracle_fusion']['base_url']
        self.api_version = config['oracle_fusion']['api_version']
        self.timeout = config['oracle_fusion']['timeout']
    
    def get_bank_accounts_simple(self):
        """Simple bank accounts fetch without complex parameters"""
        try:
            # Use the correct API version from config
            api_url = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashBankAccounts"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            params = {
                'limit': 10,
                'onlyData': 'true'
            }
            
            st.info(f"🔍 Calling API: {api_url}")
            response = self.session.get(api_url, headers=headers, params=params, timeout=self.timeout)
            
            if response.status_code == 401:
                st.error("❌ Authentication required. Please check your Oracle Fusion credentials.")
                return None
            elif response.status_code == 403:
                st.error("❌ Access forbidden. Please check your permissions.")
                return None
            elif response.status_code == 400:
                st.error(f"❌ Bad request. API version might be incorrect: {self.api_version}")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to fetch bank accounts: {e}")
            return None
    
    def test_api_versions(self):
        """Test different API versions to find the correct one"""
        versions_to_test = [
            '11.13.18.05',
            'v1',
            'latest',
            '11.13.18.06',
            '11.13.18.04'
        ]
        
        st.info("🔍 Testing different API versions...")
        
        for version in versions_to_test:
            try:
                api_url = f"{self.base_url}/fscmRestApi/resources/{version}/cashBankAccounts"
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                params = {'limit': 1}
                
                response = self.session.get(api_url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    st.success(f"✅ Version {version} works!")
                    return version
                else:
                    st.warning(f"⚠️ Version {version}: {response.status_code}")
                    
            except Exception as e:
                st.warning(f"⚠️ Version {version} failed: {str(e)[:100]}")
        
        return None

# Sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    
    # Oracle Fusion Instance Configuration
    st.subheader("🏦 Oracle Fusion Instance")
    base_url = st.text_input(
        "Base URL", 
        value=st.session_state.base_url,
        help="Your Oracle Fusion instance URL (e.g., https://your-instance.fa.ocs.oraclecloud.com)",
        key="base_url_input"
    )
    
    # Store base URL in session state
    if base_url != st.session_state.base_url:
        st.session_state.base_url = base_url
        st.info("🔄 Base URL updated - you may need to test connection again")
    
    # Show current configuration
    st.info(f"**Current Instance:** {st.session_state.base_url}")
    
    # Authentication section
    st.subheader("🔐 Authentication")
    username = st.text_input("Username", value=st.session_state.username, help="Your Oracle Fusion username", key="username_input")
    password = st.text_input("Password", value=st.session_state.password, type="password", help="Your Oracle Fusion password", key="password_input")
    
    # Store credentials in session state
    if username != st.session_state.username:
        st.session_state.username = username
    if password != st.session_state.password:
        st.session_state.password = password
    
    # Oracle connection test
    st.subheader("Oracle Connection")
    if st.button("Test Oracle Connection", key="test_connection_btn"):
        st.info("🔍 Testing connection...")
        try:
            client = SimpleOracleClient(config)
            # Add authentication if provided
            if username and password:
                client.session.auth = (username, password)
                st.info("🔐 Using provided credentials")
            
            result = client.get_bank_accounts_simple()
            if result:
                st.success("✅ Connection successful!")
                st.json(result)
            else:
                st.error("❌ Connection failed")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
    
    # Test API versions
    if st.button("Test API Versions", key="test_api_versions_btn"):
        try:
            client = SimpleOracleClient(config)
            # Add authentication if provided
            if username and password:
                client.session.auth = (username, password)
                st.info("🔐 Using provided credentials")
            
            working_version = client.test_api_versions()
            if working_version:
                st.success(f"✅ Found working version: {working_version}")
                # Update config with working version
                config['oracle_fusion']['api_version'] = working_version
            else:
                st.error("❌ No working API version found")
        except Exception as e:
            st.error(f"❌ Error testing versions: {e}")

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏦 Real Bank Accounts", 
    "💳 External Cash Transactions",
    "📄 AP Invoices", 
    "📋 AR Invoices/Receipts",
    "📊 GL Journals"
])

with tab1:
    st.success("🎯 **PRIMARY MODE - ORACLE FUSION READY**")
    st.markdown("Fetch real bank accounts and generate demo transactions")
    
    # Input parameters
    col1, col2 = st.columns(2)
    with col1:
        transactions_per_account = st.number_input(
            "Transactions per Account",
            min_value=1,
            max_value=100,
            value=st.session_state.transactions_per_account,
            help="Number of transactions to generate per bank account",
            key="transactions_per_account_tab1"
        )
    
    with col2:
        st.write("Balance Settings")
        opening_balance = st.number_input(
            "Opening Balance per Account",
            min_value=0.0,
            max_value=1000000.0,
            value=st.session_state.opening_balance,
            step=1000.0,
            help="Starting balance for each account",
            key="opening_balance_tab1"
        )
        target_closing_balance = st.number_input(
            "Target Closing Balance per Account",
            min_value=0.0,
            max_value=1000000.0,
            value=st.session_state.target_closing_balance,
            step=1000.0,
            help="Target ending balance for each account",
            key="target_closing_balance_tab1"
        )
    
    # Fetch button
    if st.button("Fetch Real Bank Accounts", type="primary", key="fetch_accounts_btn"):
        st.info("🔍 Fetching bank accounts...")
        
        try:
            client = SimpleOracleClient(config)
            
            # Add authentication if provided in sidebar
            if 'username' in st.session_state and 'password' in st.session_state:
                if st.session_state.username and st.session_state.password:
                    client.session.auth = (st.session_state.username, st.session_state.password)
                    st.info("🔐 Using stored credentials")
            
            result = client.get_bank_accounts_simple()
            
            if result and 'items' in result:
                # Store the complete raw API response
                st.session_state.raw_api_response = result
                
                # Process real accounts for display
                processed_accounts = []
                for account in result['items']:
                    processed_account = {
                        'account_id': str(account.get('BankAccountId', 'Unknown')),
                        'account_name': account.get('BankAccountName', 'Unknown Account'),
                        'account_number': account.get('BankAccountNumber', ''),
                        'bank_name': account.get('BankName', 'Unknown Bank'),
                        'currency': account.get('CurrencyCode', 'USD'),
                        'account_number_for_transactions': account.get('BankAccountNumber', '')
                    }
                    processed_accounts.append(processed_account)
                
                st.session_state.real_accounts = processed_accounts
                st.session_state.transactions_per_account = transactions_per_account
                st.session_state.opening_balance = opening_balance
                st.session_state.target_closing_balance = target_closing_balance
                
                st.success(f"✅ Fetched {len(processed_accounts)} real bank accounts!")
            else:
                st.error("❌ No accounts found or API error")
                
        except Exception as e:
            st.error(f"❌ Error fetching accounts: {e}")
            # Fallback to fake data
            st.info("🔄 Using demo data as fallback...")
            fake_accounts = [
                {
                    'account_id': '300000004068939',
                    'account_name': 'Main Operating Account',
                    'account_number': '1234567890',
                    'bank_name': 'Test Bank',
                    'currency': 'USD',
                    'account_number_for_transactions': '1234567890'
                },
                {
                    'account_id': '300000004068940',
                    'account_name': 'Secondary Account',
                    'account_number': '0987654321',
                    'bank_name': 'Test Bank 2',
                    'currency': 'USD',
                    'account_number_for_transactions': '0987654321'
                }
            ]
            st.session_state.real_accounts = fake_accounts
            st.session_state.transactions_per_account = transactions_per_account
            st.session_state.opening_balance = opening_balance
            st.session_state.target_closing_balance = target_closing_balance
            st.success(f"✅ Using {len(fake_accounts)} demo accounts!")
    
    # Display accounts if available
    if st.session_state.real_accounts:
        st.subheader("📋 Bank Accounts")
        
        # Create display dataframe
        display_data = []
        for account in st.session_state.real_accounts:
            display_data.append({
                'Account ID': str(account['account_id']),
                'Account Name': account['account_name'],
                'Account Number': account['account_number_for_transactions'],
                'Bank Name': account['bank_name'],
                'Currency': account['currency']
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
        
        # Download complete raw API response
        if 'raw_api_response' in st.session_state:
            import json
            raw_json_data = json.dumps(st.session_state.raw_api_response, indent=2)
            st.download_button(
                label="📥 Download Complete Raw JSON",
                data=raw_json_data,
                file_name="oracle_bank_accounts_complete.json",
                mime="application/json"
            )
            
            # Also show a preview of the raw data
            with st.expander("🔍 Raw API Response Preview"):
                st.json(st.session_state.raw_api_response)
        
        # Download processed data (simplified)
        import json
        processed_json_data = json.dumps(st.session_state.real_accounts, indent=2)
        st.download_button(
            label="📥 Download Processed JSON",
            data=processed_json_data,
            file_name="bank_accounts_processed.json",
            mime="application/json"
        )
        
        # Generate transactions button
        if st.button("Generate Demo Transactions", type="primary", key="generate_transactions_btn"):
            st.info("🔄 Generating transactions...")
            
            # Generate fake transactions
            all_transactions = []
            for account in st.session_state.real_accounts:
                for i in range(st.session_state.transactions_per_account):
                    transaction = {
                        'account_id': account['account_id'],
                        'account_name': account['account_name'],
                        'transaction_id': f"TXN{i+1:03d}",
                        'date': f"2024-01-{(i+1):02d}",
                        'description': f"Demo transaction {i+1}",
                        'amount': round(1000 + (i * 100), 2),
                        'type': 'Credit' if i % 2 == 0 else 'Debit'
                    }
                    all_transactions.append(transaction)
            
            # Display transactions
            st.subheader("📊 Generated Transactions")
            transactions_df = pd.DataFrame(all_transactions)
            st.dataframe(transactions_df, use_container_width=True)
            
            # Download transactions
            csv_data = transactions_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Transactions CSV",
                data=csv_data,
                file_name="demo_transactions.csv",
                mime="text/csv"
            )
            
            st.success(f"✅ Generated {len(all_transactions)} transactions!")
        
        # BAI2 Generation button
        if bai2_gen and st.button("Generate BAI2 Bank Statement", type="primary", key="generate_bai2_btn"):
            st.info("🏦 Generating BAI2 bank statement...")
            
            try:
                # Generate BAI2 content
                bai2_content = bai2_gen.generate_bai2_file(
                    accounts=st.session_state.real_accounts,
                    transactions_per_account=st.session_state.transactions_per_account,
                    opening_balance=st.session_state.opening_balance,
                    target_closing_balance=st.session_state.target_closing_balance
                )
                
                # Display BAI2 preview
                st.subheader("🏦 BAI2 Bank Statement")
                with st.expander("📋 BAI2 Content Preview"):
                    st.code(bai2_content, language="text")
                
                # Download BAI2 file
                st.download_button(
                    label="📥 Download BAI2 File",
                    data=bai2_content,
                    file_name="bank_statement.bai2",
                    mime="text/plain"
                )
                
                st.success("✅ BAI2 bank statement generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating BAI2: {e}")

# External Cash Transactions Tab
with tab2:
    st.success("💳 **EXTERNAL CASH TRANSACTIONS**")
    st.markdown("Generate external cash management transactions for Oracle Fusion")
    
    # Check if we have bank accounts
    if not st.session_state.real_accounts:
        st.warning("⚠️ Please fetch bank accounts from the 'Real Bank Accounts' tab first")
    else:
        # Input parameters
        col1, col2 = st.columns(2)
        with col1:
            external_transactions_per_account = st.number_input(
                "External Transactions per Account",
                min_value=1,
                max_value=20,
                value=st.session_state.external_transactions_per_account,
                help="Number of external transactions to generate per bank account",
                key="external_transactions_per_account_tab2"
            )
        
        with col2:
            date_range_days = st.number_input(
                "Date Range (Days)",
                min_value=1,
                max_value=90,
                value=30,
                help="Number of days back to generate transactions",
                key="date_range_days_tab2"
            )
        
        # Generate external transactions button
        if external_cash_gen and st.button("Generate External Cash Transactions", type="primary", key="generate_external_btn"):
            st.info("💳 Generating external cash transactions...")
            
            try:
                # Generate external transactions
                external_transactions = external_cash_gen.generate_external_transactions(
                    accounts=st.session_state.real_accounts,
                    transactions_per_account=external_transactions_per_account,
                    date_range_days=date_range_days
                )
                
                # Store in session state
                st.session_state.external_transactions = external_transactions
                st.session_state.external_transactions_per_account = external_transactions_per_account
                
                # Display transactions
                st.subheader("📊 External Cash Transactions")
                transactions_df = pd.DataFrame(external_transactions)
                st.dataframe(transactions_df, use_container_width=True)
                
                # Download CSV
                csv_data = external_cash_gen.generate_csv_content(external_transactions)
                st.download_button(
                    label="📥 Download External Transactions CSV",
                    data=csv_data,
                    file_name="external_cash_transactions.csv",
                    mime="text/csv"
                )
                
                # Download Oracle Fusion format
                fusion_format = external_cash_gen.generate_oracle_fusion_format(external_transactions)
                import json
                fusion_json = json.dumps(fusion_format, indent=2)
                st.download_button(
                    label="📥 Download Oracle Fusion JSON",
                    data=fusion_json,
                    file_name="external_transactions_fusion.json",
                    mime="application/json"
                )
                
                st.success(f"✅ Generated {len(external_transactions)} external cash transactions!")
                
            except Exception as e:
                st.error(f"❌ Error generating external transactions: {e}")
        
        # Display existing transactions if available
        if st.session_state.external_transactions:
            st.subheader("📋 Previously Generated External Transactions")
            existing_df = pd.DataFrame(st.session_state.external_transactions)
            st.dataframe(existing_df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_amount = sum(t['Amount'] for t in st.session_state.external_transactions)
                st.metric("Total Amount", f"${total_amount:,.2f}")
            
            with col2:
                credit_count = len([t for t in st.session_state.external_transactions if t['Amount'] > 0])
                st.metric("Credit Transactions", credit_count)
            
            with col3:
                debit_count = len([t for t in st.session_state.external_transactions if t['Amount'] < 0])
                st.metric("Debit Transactions", debit_count)

# AP Invoices Tab
with tab3:
    st.success("📄 **AP INVOICES**")
    st.markdown("Generate AP (Accounts Payable) invoices for Oracle Fusion")
    
    # Check if we have bank accounts
    if not st.session_state.real_accounts:
        st.warning("⚠️ Please fetch bank accounts from the 'Real Bank Accounts' tab first")
    else:
        # Input parameters
        col1, col2, col3 = st.columns(3)
        with col1:
            ap_invoices_per_account = st.number_input(
                "AP Invoices per Account",
                min_value=1,
                max_value=10,
                value=st.session_state.ap_invoices_per_account,
                help="Number of AP invoices to generate per bank account",
                key="ap_invoices_per_account_tab3"
            )
        
        with col2:
            ap_lines_per_invoice = st.number_input(
                "Lines per Invoice",
                min_value=1,
                max_value=10,
                value=st.session_state.ap_lines_per_invoice,
                help="Number of line items per AP invoice",
                key="ap_lines_per_invoice_tab3"
            )
        
        with col3:
            ap_date_range_days = st.number_input(
                "Date Range (Days)",
                min_value=1,
                max_value=90,
                value=30,
                help="Number of days back to generate invoices",
                key="ap_date_range_days_tab3"
            )
        
        # Generate AP invoices button
        if ap_invoice_gen and st.button("Generate AP Invoices", type="primary", key="generate_ap_btn"):
            st.info("📄 Generating AP invoices...")
            
            try:
                # Generate AP invoices
                ap_invoices = ap_invoice_gen.generate_ap_invoices(
                    accounts=st.session_state.real_accounts,
                    invoices_per_account=ap_invoices_per_account,
                    lines_per_invoice=ap_lines_per_invoice,
                    date_range_days=ap_date_range_days
                )
                
                # Store in session state
                st.session_state.ap_invoices = ap_invoices
                st.session_state.ap_invoices_per_account = ap_invoices_per_account
                st.session_state.ap_lines_per_invoice = ap_lines_per_invoice
                
                # Display invoice summary
                st.subheader("📊 AP Invoices Summary")
                
                # Create summary dataframe
                summary_data = []
                for invoice in ap_invoices:
                    header = invoice['header']
                    summary_data.append({
                        'Invoice ID': header['InvoiceId'],
                        'Invoice Number': header['InvoiceNumber'],
                        'Supplier': header['SupplierName'],
                        'Amount': f"${header['InvoiceAmount']:,.2f}",
                        'Currency': header['Currency'],
                        'Invoice Date': header['InvoiceDate'],
                        'Due Date': header['DueDate'],
                        'Status': header['Status'],
                        'Lines': len(invoice['lines'])
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
                
                # Download CSV
                csv_data = ap_invoice_gen.generate_csv_content(ap_invoices)
                st.download_button(
                    label="📥 Download AP Invoices CSV",
                    data=csv_data,
                    file_name="ap_invoices_interface.csv",
                    mime="text/csv"
                )
                
                # Download Oracle Fusion format
                fusion_format = ap_invoice_gen.generate_oracle_fusion_format(ap_invoices)
                import json
                fusion_json = json.dumps(fusion_format, indent=2)
                st.download_button(
                    label="📥 Download Oracle Fusion JSON",
                    data=fusion_json,
                    file_name="ap_invoices_fusion.json",
                    mime="application/json"
                )
                
                # Download Properties file
                properties_data = ap_invoice_gen.generate_properties_content(ap_invoices)
                st.download_button(
                    label="📥 Download Properties File",
                    data=properties_data,
                    file_name="ap_invoice_import.properties",
                    mime="text/plain"
                )
                
                st.success(f"✅ Generated {len(ap_invoices)} AP invoices!")
                
            except Exception as e:
                st.error(f"❌ Error generating AP invoices: {e}")
        
        # Display existing invoices if available
        if st.session_state.ap_invoices:
            st.subheader("📋 Previously Generated AP Invoices")
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_invoices = len(st.session_state.ap_invoices)
                st.metric("Total Invoices", total_invoices)
            
            with col2:
                total_amount = sum(inv['header']['InvoiceAmount'] for inv in st.session_state.ap_invoices)
                st.metric("Total Amount", f"${total_amount:,.2f}")
            
            with col3:
                total_lines = sum(len(inv['lines']) for inv in st.session_state.ap_invoices)
                st.metric("Total Line Items", total_lines)
            
            with col4:
                avg_amount = total_amount / total_invoices if total_invoices > 0 else 0
                st.metric("Average Invoice", f"${avg_amount:,.2f}")
            
            # Show detailed invoice data
            with st.expander("📄 Detailed Invoice Data"):
                for i, invoice in enumerate(st.session_state.ap_invoices):
                    header = invoice['header']
                    st.write(f"**Invoice {i+1}: {header['InvoiceId']}**")
                    st.write(f"Supplier: {header['SupplierName']} | Amount: ${header['InvoiceAmount']:,.2f}")
                    
                    # Show lines
                    lines_df = pd.DataFrame(invoice['lines'])
                    st.dataframe(lines_df, use_container_width=True)
                    st.write("---")

# AR Invoices/Receipts Tab
with tab4:
    st.success("📋 **AR INVOICES/RECEIPTS**")
    st.markdown("Generate AR (Accounts Receivable) invoices and receipts for Oracle Fusion")
    
    # Check if we have bank accounts
    if not st.session_state.real_accounts:
        st.warning("⚠️ Please fetch bank accounts from the 'Real Bank Accounts' tab first")
    else:
        # Input parameters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ar_invoices_per_account = st.number_input(
                "AR Invoices per Account",
                min_value=1,
                max_value=10,
                value=st.session_state.ar_invoices_per_account,
                help="Number of AR invoices to generate per bank account",
                key="ar_invoices_per_account_tab4"
            )
        
        with col2:
            ar_lines_per_invoice = st.number_input(
                "Lines per Invoice",
                min_value=1,
                max_value=10,
                value=st.session_state.ar_lines_per_invoice,
                help="Number of line items per AR invoice",
                key="ar_lines_per_invoice_tab4"
            )
        
        with col3:
            ar_date_range_days = st.number_input(
                "Date Range (Days)",
                min_value=1,
                max_value=90,
                value=30,
                help="Number of days back to generate invoices",
                key="ar_date_range_days_tab4"
            )
        
        with col4:
            receipt_percentage = st.slider(
                "Receipt Percentage",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Percentage of invoices that will have receipts",
                key="receipt_percentage_tab4"
            )
        
        # Generate AR invoices button
        if ar_invoice_gen and st.button("Generate AR Invoices & Receipts", type="primary", key="generate_ar_btn"):
            st.info("📋 Generating AR invoices and receipts...")
            
            try:
                # Generate AR invoices
                ar_invoices = ar_invoice_gen.generate_ar_invoices(
                    accounts=st.session_state.real_accounts,
                    invoices_per_account=ar_invoices_per_account,
                    lines_per_invoice=ar_lines_per_invoice,
                    date_range_days=ar_date_range_days
                )
                
                # Generate receipts for invoices
                ar_receipts = ar_invoice_gen.generate_receipts(
                    invoices=ar_invoices,
                    receipt_percentage=receipt_percentage
                )
                
                # Store in session state
                st.session_state.ar_invoices = ar_invoices
                st.session_state.ar_receipts = ar_receipts
                st.session_state.ar_invoices_per_account = ar_invoices_per_account
                st.session_state.ar_lines_per_invoice = ar_lines_per_invoice
                
                # Display invoice summary
                st.subheader("📊 AR Invoices Summary")
                
                # Create summary dataframe
                summary_data = []
                for invoice in ar_invoices:
                    header = invoice['header']
                    has_receipt = any(r['InvoiceId'] == header['InvoiceId'] for r in ar_receipts)
                    summary_data.append({
                        'Invoice ID': header['InvoiceId'],
                        'Invoice Number': header['InvoiceNumber'],
                        'Customer': header['CustomerName'],
                        'Amount': f"${header['InvoiceAmount']:,.2f}",
                        'Currency': header['Currency'],
                        'Invoice Date': header['InvoiceDate'],
                        'Due Date': header['DueDate'],
                        'Status': header['Status'],
                        'Payment Terms': header['PaymentTerms'],
                        'Lines': len(invoice['lines']),
                        'Has Receipt': '✅ Yes' if has_receipt else '❌ No'
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
                
                # Display receipts summary
                if ar_receipts:
                    st.subheader("💰 AR Receipts Summary")
                    receipts_data = []
                    for receipt in ar_receipts:
                        receipts_data.append({
                            'Receipt ID': receipt['ReceiptId'],
                            'Invoice ID': receipt['InvoiceId'],
                            'Customer': receipt['CustomerName'],
                            'Amount': f"${receipt['Amount']:,.2f}",
                            'Receipt Date': receipt['ReceiptDate'],
                            'Payment Method': receipt['PaymentMethod'],
                            'Status': receipt['Status']
                        })
                    
                    receipts_df = pd.DataFrame(receipts_data)
                    st.dataframe(receipts_df, use_container_width=True)
                
                # Download CSV files
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download AR Invoices CSV
                    csv_data = ar_invoice_gen.generate_csv_content(ar_invoices)
                    st.download_button(
                        label="📥 Download AR Invoices CSV",
                        data=csv_data,
                        file_name="ar_invoices_interface.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Download AR Receipts CSV
                    if ar_receipts:
                        receipts_csv_data = ar_invoice_gen.generate_receipts_csv_content(ar_receipts)
                        st.download_button(
                            label="📥 Download AR Receipts CSV",
                            data=receipts_csv_data,
                            file_name="ar_receipts_interface.csv",
                            mime="text/csv"
                        )
                
                # Download Oracle Fusion format
                fusion_format = ar_invoice_gen.generate_oracle_fusion_format(ar_invoices)
                import json
                fusion_json = json.dumps(fusion_format, indent=2)
                st.download_button(
                    label="📥 Download Oracle Fusion JSON",
                    data=fusion_json,
                    file_name="ar_invoices_fusion.json",
                    mime="application/json"
                )
                
                st.success(f"✅ Generated {len(ar_invoices)} AR invoices and {len(ar_receipts)} receipts!")
                
            except Exception as e:
                st.error(f"❌ Error generating AR invoices: {e}")
        
        # Display existing invoices if available
        if st.session_state.ar_invoices:
            st.subheader("📋 Previously Generated AR Data")
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_invoices = len(st.session_state.ar_invoices)
                st.metric("Total Invoices", total_invoices)
            
            with col2:
                total_amount = sum(inv['header']['InvoiceAmount'] for inv in st.session_state.ar_invoices)
                st.metric("Total Invoice Amount", f"${total_amount:,.2f}")
            
            with col3:
                total_receipts = len(st.session_state.ar_receipts)
                st.metric("Total Receipts", total_receipts)
            
            with col4:
                total_receipt_amount = sum(r['Amount'] for r in st.session_state.ar_receipts)
                st.metric("Total Receipt Amount", f"${total_receipt_amount:,.2f}")
            
            # Show detailed invoice data
            with st.expander("📄 Detailed AR Invoice Data"):
                for i, invoice in enumerate(st.session_state.ar_invoices):
                    header = invoice['header']
                    st.write(f"**Invoice {i+1}: {header['InvoiceId']}**")
                    st.write(f"Customer: {header['CustomerName']} | Amount: ${header['InvoiceAmount']:,.2f} | Payment Terms: {header['PaymentTerms']}")
                    
                    # Show lines
                    lines_df = pd.DataFrame(invoice['lines'])
                    st.dataframe(lines_df, use_container_width=True)
                    st.write("---")

# GL Journals Tab
with tab5:
    st.success("📊 **GL JOURNALS**")
    st.markdown("Generate GL (General Ledger) journal entries for Oracle Fusion")
    
    # Check if we have bank accounts
    if not st.session_state.real_accounts:
        st.warning("⚠️ Please fetch bank accounts from the 'Real Bank Accounts' tab first")
    else:
        # Input parameters
        col1, col2, col3 = st.columns(3)
        with col1:
            gl_journals_per_account = st.number_input(
                "GL Journals per Account",
                min_value=1,
                max_value=10,
                value=st.session_state.gl_journals_per_account,
                help="Number of GL journals to generate per bank account",
                key="gl_journals_per_account_tab5"
            )
        
        with col2:
            gl_lines_per_journal = st.number_input(
                "Lines per Journal",
                min_value=2,
                max_value=10,
                value=st.session_state.gl_lines_per_journal,
                help="Number of line items per GL journal (minimum 2 for balance)",
                key="gl_lines_per_journal_tab5"
            )
        
        with col3:
            gl_date_range_days = st.number_input(
                "Date Range (Days)",
                min_value=1,
                max_value=90,
                value=30,
                help="Number of days back to generate journals",
                key="gl_date_range_days_tab5"
            )
        
        # Generate GL journals button
        if gl_journal_gen and st.button("Generate GL Journals", type="primary", key="generate_gl_btn"):
            st.info("📊 Generating GL journals...")
            
            try:
                # Generate GL journals
                gl_journals = gl_journal_gen.generate_gl_journals(
                    accounts=st.session_state.real_accounts,
                    journals_per_account=gl_journals_per_account,
                    lines_per_journal=gl_lines_per_journal,
                    date_range_days=gl_date_range_days
                )
                
                # Store in session state
                st.session_state.gl_journals = gl_journals
                st.session_state.gl_journals_per_account = gl_journals_per_account
                st.session_state.gl_lines_per_journal = gl_lines_per_journal
                
                # Display journal summary
                st.subheader("📊 GL Journals Summary")
                
                # Create summary dataframe
                summary_data = []
                for journal in gl_journals:
                    header = journal['header']
                    is_balanced = abs(header['TotalDebit'] - header['TotalCredit']) < 0.01
                    summary_data.append({
                        'Journal ID': header['JournalId'],
                        'Journal Name': header['JournalName'],
                        'Journal Type': header['JournalType'],
                        'Business Unit': header['BusinessUnit'],
                        'Ledger': header['Ledger'],
                        'Currency': header['Currency'],
                        'Total Debit': f"${header['TotalDebit']:,.2f}",
                        'Total Credit': f"${header['TotalCredit']:,.2f}",
                        'Lines': len(journal['lines']),
                        'Balanced': '✅ Yes' if is_balanced else '❌ No'
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
                
                # Download CSV
                csv_data = gl_journal_gen.generate_csv_content(gl_journals)
                st.download_button(
                    label="📥 Download GL Journals CSV",
                    data=csv_data,
                    file_name="gl_journals_interface.csv",
                    mime="text/csv"
                )
                
                # Download Oracle Fusion format
                fusion_format = gl_journal_gen.generate_oracle_fusion_format(gl_journals)
                import json
                fusion_json = json.dumps(fusion_format, indent=2)
                st.download_button(
                    label="📥 Download Oracle Fusion JSON",
                    data=fusion_json,
                    file_name="gl_journals_fusion.json",
                    mime="application/json"
                )
                
                # Download Properties file
                properties_data = gl_journal_gen.generate_properties_content(gl_journals)
                st.download_button(
                    label="📥 Download Properties File",
                    data=properties_data,
                    file_name="gl_journal_import.properties",
                    mime="text/plain"
                )
                
                st.success(f"✅ Generated {len(gl_journals)} GL journals!")
                
            except Exception as e:
                st.error(f"❌ Error generating GL journals: {e}")
        
        # Display existing journals if available
        if st.session_state.gl_journals:
            st.subheader("📋 Previously Generated GL Journals")
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_journals = len(st.session_state.gl_journals)
                st.metric("Total Journals", total_journals)
            
            with col2:
                total_lines = sum(len(journal['lines']) for journal in st.session_state.gl_journals)
                st.metric("Total Lines", total_lines)
            
            with col3:
                total_debit = sum(journal['header']['TotalDebit'] for journal in st.session_state.gl_journals)
                st.metric("Total Debit", f"${total_debit:,.2f}")
            
            with col4:
                total_credit = sum(journal['header']['TotalCredit'] for journal in st.session_state.gl_journals)
                st.metric("Total Credit", f"${total_credit:,.2f}")
            
            # Check overall balance
            if abs(total_debit - total_credit) < 0.01:
                st.success("✅ All journals are balanced!")
            else:
                st.error("❌ Journals are not balanced!")
            
            # Show detailed journal data
            with st.expander("📄 Detailed GL Journal Data"):
                for i, journal in enumerate(st.session_state.gl_journals):
                    header = journal['header']
                    st.write(f"**Journal {i+1}: {header['JournalId']}**")
                    st.write(f"Type: {header['JournalType']} | Business Unit: {header['BusinessUnit']} | Ledger: {header['Ledger']}")
                    st.write(f"Total Debit: ${header['TotalDebit']:,.2f} | Total Credit: ${header['TotalCredit']:,.2f}")
                    
                    # Show lines
                    lines_df = pd.DataFrame(journal['lines'])
                    st.dataframe(lines_df, use_container_width=True)
                    st.write("---") 