"""
Oracle Fusion Demo Transaction Generator
Main Streamlit application for generating demo transactions
"""

import streamlit as st
import pandas as pd
import json
import yaml
from datetime import datetime
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.oracle_client import OracleFusionClient
from generators.bai2_generator import BAI2Generator
from generators.transaction_generators import TransactionGenerators
from generators.real_bank_generator import RealBankGenerator
from utils.excel_exporter import ExcelExporter

# Page configuration
st.set_page_config(
    page_title="Oracle Fusion Demo Transaction Generator",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_config():
    """Load configuration from YAML file"""
    try:
        with open("config/config.yaml", 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error("Configuration file not found. Please ensure config/config.yaml exists.")
        return None

def main():
    """Main application function"""
    st.title("🏦 Oracle Fusion Demo Transaction Generator")
    st.markdown("Generate demo transactions for Oracle Fusion Financials testing")
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Oracle Fusion Connection
    st.sidebar.subheader("Oracle Fusion Connection")
    base_url = st.sidebar.text_input(
        "Base URL",
        value=config['oracle_fusion']['base_url'],
        help="Your Oracle Fusion instance URL"
    )
    username = st.sidebar.text_input("Username", type="default")
    password = st.sidebar.text_input("Password", type="password")
    
    # Test connection button
    if st.sidebar.button("Test Connection"):
        if base_url and username and password:
            try:
                client = OracleFusionClient(base_url, username, password)
                if client.authenticate():
                    st.sidebar.success("✅ Connection successful!")
                else:
                    st.sidebar.error("❌ Connection failed!")
            except Exception as e:
                st.sidebar.error(f"❌ Connection error: {str(e)}")
        else:
            st.sidebar.warning("Please enter all connection details")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Bank Statements", "Real Bank Accounts", "AP Invoices", "AR Invoices", "GL Journals", "Export Data"
    ])
    
    # Initialize generators
    bai2_gen = BAI2Generator()
    transaction_gen = TransactionGenerators()
    real_bank_gen = RealBankGenerator()
    excel_exporter = ExcelExporter()
    
    # Tab 1: Bank Statements
    with tab1:
        st.header("🏦 Bank Statement Generator")
        st.markdown("Generate BAI2 format bank statements with opening/closing balances")
        
        col1, col2 = st.columns(2)
        
        with col1:
            account_count = st.number_input(
                "Number of Bank Accounts",
                min_value=1,
                max_value=10,
                value=3,
                help="Number of bank accounts to generate"
            )
            
            transactions_per_account = st.number_input(
                "Transactions per Account",
                min_value=5,
                max_value=100,
                value=config['transactions']['bank_statement']['default_count'],
                help="Number of transactions per bank account"
            )
        
        with col2:
            min_amount = st.number_input(
                "Minimum Transaction Amount",
                min_value=1.0,
                max_value=1000.0,
                value=float(config['transactions']['bank_statement']['min_amount']),
                help="Minimum transaction amount"
            )
            
            max_amount = st.number_input(
                "Maximum Transaction Amount",
                min_value=1000.0,
                max_value=50000.0,
                value=float(config['transactions']['bank_statement']['max_amount']),
                help="Maximum transaction amount"
            )
        
        if st.button("Generate Bank Statement", type="primary"):
            with st.spinner("Generating bank statement..."):
                try:
                    # Generate bank statement
                    bai2_file = bai2_gen.generate_demo_bank_statement(
                        account_count=account_count,
                        transactions_per_account=transactions_per_account
                    )
                    
                    st.success(f"✅ Bank statement generated: {bai2_file}")
                    
                    # Show preview
                    with open(bai2_file, 'r') as f:
                        bai2_content = f.read()
                    
                    st.subheader("BAI2 File Preview")
                    st.code(bai2_content[:1000] + "..." if len(bai2_content) > 1000 else bai2_content)
                    
                    # Download button
                    st.download_button(
                        label="Download BAI2 File",
                        data=bai2_content,
                        file_name=bai2_file,
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating bank statement: {str(e)}")
    
    # Tab 2: Real Bank Accounts
    with tab2:
        st.header("🏦 Real Bank Account Generator")
        st.markdown("Generate bank statements using real bank accounts from your Oracle Fusion instance")
        
        if st.button("Fetch Real Bank Accounts", type="primary"):
            if base_url and username and password:
                with st.spinner("Fetching real bank accounts from Oracle Fusion..."):
                    try:
                        # Create Oracle client
                        client = OracleFusionClient(base_url, username, password)
                        
                        # Test connection first
                        if client.authenticate():
                            # Fetch real bank accounts
                            result = client.get_bank_accounts()
                            
                            if result['success']:
                                # Process real accounts
                                real_accounts = real_bank_gen.process_real_bank_accounts(result['data'])
                                
                                if real_accounts:
                                    st.success(f"✅ Fetched {len(real_accounts)} real bank accounts")
                                    
                                    # Display real accounts
                                    st.subheader("Real Bank Accounts Found")
                                    account_data = []
                                    for account in real_accounts:
                                        account_data.append({
                                            'Account ID': account['account_id'],
                                            'Account Name': account['account_name'],
                                            'Account Number': account['account_number'],
                                            'Bank Name': account['bank_name'],
                                            'Currency': account['currency'],
                                            'Status': 'Active' if account['is_active'] else 'Inactive'
                                        })
                                    
                                    df = pd.DataFrame(account_data)
                                    st.dataframe(df)
                                    
                                    # Generate transactions for real accounts
                                    transactions_per_account = st.number_input(
                                        "Transactions per Account",
                                        min_value=5,
                                        max_value=100,
                                        value=config['transactions']['bank_statement']['default_count'],
                                        key="real_transactions"
                                    )
                                    
                                    if st.button("Generate BAI2 with Real Accounts", type="primary"):
                                        with st.spinner("Generating BAI2 file with real accounts..."):
                                            try:
                                                # Generate BAI2 file with real accounts
                                                bai2_file = real_bank_gen.create_bai2_with_real_accounts(
                                                    real_accounts, transactions_per_account
                                                )
                                                
                                                st.success(f"✅ BAI2 file generated: {bai2_file}")
                                                
                                                # Show preview
                                                with open(bai2_file, 'r') as f:
                                                    bai2_content = f.read()
                                                
                                                st.subheader("BAI2 File Preview")
                                                st.code(bai2_content[:1000] + "..." if len(bai2_content) > 1000 else bai2_content)
                                                
                                                # Download button
                                                st.download_button(
                                                    label="Download BAI2 File",
                                                    data=bai2_content,
                                                    file_name=bai2_file,
                                                    mime="text/plain"
                                                )
                                                
                                                # Generate external transactions
                                                external_transactions = real_bank_gen.create_external_transactions_for_real_accounts(
                                                    real_accounts, transactions_per_account
                                                )
                                                
                                                st.subheader("External Cash Transactions")
                                                st.dataframe(pd.DataFrame(external_transactions))
                                                
                                            except Exception as e:
                                                st.error(f"Error generating BAI2 with real accounts: {str(e)}")
                                    
                                else:
                                    st.warning("No bank accounts found or error processing accounts")
                            else:
                                st.error(f"Failed to fetch bank accounts: {result.get('error', 'Unknown error')}")
                        else:
                            st.error("Failed to authenticate with Oracle Fusion")
                            
                    except Exception as e:
                        st.error(f"Error connecting to Oracle Fusion: {str(e)}")
            else:
                st.warning("Please enter Oracle Fusion connection details in the sidebar")
    
    # Tab 3: AP Invoices
    with tab3:
        st.header("📄 AP Invoice Generator")
        st.markdown("Generate Accounts Payable invoices")
        
        ap_count = st.number_input(
            "Number of AP Invoices",
            min_value=1,
            max_value=50,
            value=config['transactions']['ap_invoices']['default_count'],
            help="Number of AP invoices to generate"
        )
        
        if st.button("Generate AP Invoices", type="primary"):
            with st.spinner("Generating AP invoices..."):
                try:
                    ap_invoices = transaction_gen.generate_ap_invoices(ap_count)
                    
                    st.success(f"✅ Generated {len(ap_invoices)} AP invoices")
                    
                    # Show preview
                    df = pd.DataFrame(ap_invoices)
                    st.dataframe(df.head(10))
                    
                    # Export to Excel
                    excel_file = excel_exporter.export_ap_invoices(ap_invoices)
                    
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label="Download Excel File",
                            data=f.read(),
                            file_name=excel_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                except Exception as e:
                    st.error(f"Error generating AP invoices: {str(e)}")
    
    # Tab 4: AR Invoices
    with tab4:
        st.header("📄 AR Invoice Generator")
        st.markdown("Generate Accounts Receivable invoices")
        
        ar_count = st.number_input(
            "Number of AR Invoices",
            min_value=1,
            max_value=50,
            value=config['transactions']['ar_invoices']['default_count'],
            help="Number of AR invoices to generate"
        )
        
        if st.button("Generate AR Invoices", type="primary"):
            with st.spinner("Generating AR invoices..."):
                try:
                    ar_invoices = transaction_gen.generate_ar_invoices(ar_count)
                    
                    st.success(f"✅ Generated {len(ar_invoices)} AR invoices")
                    
                    # Show preview
                    df = pd.DataFrame(ar_invoices)
                    st.dataframe(df.head(10))
                    
                    # Export to Excel
                    excel_file = excel_exporter.export_ar_invoices(ar_invoices)
                    
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label="Download Excel File",
                            data=f.read(),
                            file_name=excel_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                except Exception as e:
                    st.error(f"Error generating AR invoices: {str(e)}")
    
    # Tab 5: GL Journals
    with tab5:
        st.header("📊 GL Journal Generator")
        st.markdown("Generate General Ledger journal entries")
        
        gl_count = st.number_input(
            "Number of GL Journals",
            min_value=1,
            max_value=50,
            value=config['transactions']['gl_journals']['default_count'],
            help="Number of GL journal entries to generate"
        )
        
        if st.button("Generate GL Journals", type="primary"):
            with st.spinner("Generating GL journals..."):
                try:
                    gl_journals = transaction_gen.generate_gl_journals(gl_count)
                    
                    st.success(f"✅ Generated {len(gl_journals)} GL journal entries")
                    
                    # Show preview
                    df = pd.DataFrame(gl_journals)
                    st.dataframe(df.head(10))
                    
                    # Export to Excel
                    excel_file = excel_exporter.export_gl_journals(gl_journals)
                    
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label="Download Excel File",
                            data=f.read(),
                            file_name=excel_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                except Exception as e:
                    st.error(f"Error generating GL journals: {str(e)}")
    
    # Tab 6: Export Data
    with tab6:
        st.header("📤 Export Data")
        st.markdown("Export all generated data to various formats")
        
        # Generate all transaction types
        if st.button("Generate All Transaction Types", type="primary"):
            with st.spinner("Generating all transaction types..."):
                try:
                    # Generate all types
                    external_transactions = transaction_gen.generate_external_cash_transactions()
                    ap_invoices = transaction_gen.generate_ap_invoices()
                    ar_invoices = transaction_gen.generate_ar_invoices()
                    gl_journals = transaction_gen.generate_gl_journals()
                    ar_receipts = transaction_gen.generate_ar_receipts()
                    
                    # Combine all data
                    all_data = {
                        'external_cash_transactions': external_transactions,
                        'ap_invoices': ap_invoices,
                        'ar_invoices': ar_invoices,
                        'gl_journals': gl_journals,
                        'ar_receipts': ar_receipts
                    }
                    
                    # Export to Excel
                    excel_file = excel_exporter.export_transaction_data(all_data)
                    
                    st.success(f"✅ Generated and exported all transaction types")
                    
                    # Show summary
                    summary_data = []
                    for transaction_type, transactions in all_data.items():
                        summary_data.append({
                            'Transaction Type': transaction_type.replace('_', ' ').title(),
                            'Count': len(transactions),
                            'Total Amount': sum(t.get('amount', 0) for t in transactions)
                        })
                    
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df)
                    
                    # Download button
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label="Download Complete Excel File",
                            data=f.read(),
                            file_name=excel_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                except Exception as e:
                    st.error(f"Error generating all transaction types: {str(e)}")

if __name__ == "__main__":
    main() 