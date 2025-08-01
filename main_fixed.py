import streamlit as st
import pandas as pd
import yaml
import os
import requests
import gzip
import base64
import xml.etree.ElementTree as ET
from pathlib import Path
from io import BytesIO
import re

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
# Per-account balances are now handled in the account objects themselves
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'password' not in st.session_state:
    st.session_state.password = ""
if 'base_url' not in st.session_state:
    st.session_state.base_url = "https://your-instance.fa.ocs.oraclecloud.com"
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
if 'bai2_content' not in st.session_state:
    st.session_state.bai2_content = None

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
    
    def extract_balance_from_bank_account(self, account_data):
        """Extract balance information from bank account data"""
        try:
            # List of possible balance field names in bank account data
            balance_fields = [
                'OpeningBalance', 'CurrentBalance', 'Balance', 'AccountBalance', 
                'LedgerBalance', 'BookBalance', 'AvailableBalance', 'RunningBalance',
                'CashBalance', 'CashManagementBalance', 'CashManagementCashBalance',
                'CashBalanceAmount', 'CashManagementAmount', 'CashManagementCashBalanceAmount',
                'CashManagementCashBalanceValue', 'AccountBalanceAmount', 'CurrentBalanceAmount',
                'OpeningBalanceAmount', 'BookBalanceAmount', 'LedgerBalanceAmount'
            ]
            
            # Check direct fields
            for field in balance_fields:
                if field in account_data and account_data[field] is not None:
                    try:
                        balance = float(account_data[field])
                        if balance > 0:
                            return balance, field
                    except (ValueError, TypeError):
                        continue
            
            # Check nested objects
            nested_objects = ['Balance', 'CashManagement', 'CashBalance', 'AccountBalance']
            for obj_name in nested_objects:
                if obj_name in account_data and isinstance(account_data[obj_name], dict):
                    for field in balance_fields:
                        if field in account_data[obj_name] and account_data[obj_name][field] is not None:
                            try:
                                balance = float(account_data[obj_name][field])
                                if balance > 0:
                                    return balance, f"{obj_name}.{field}"
                            except (ValueError, TypeError):
                                continue
            
            return 0.0, "No balance found"
            
        except Exception as e:
            st.warning(f"Error extracting balance from account: {e}")
            return 0.0, "Error"
    
    def extract_account_combination_from_bank_account(self, account_data):
        """Extract account combination from bank account data"""
        try:
            # Try different possible field names for account combination
            combination_fields = [
                'CashAccountCombination', 'AccountCombination', 'GLAccountCombination',
                'DetailAccountCombination', 'AccountCode', 'GLAccountCode'
            ]
            
            for field in combination_fields:
                if field in account_data and account_data[field]:
                    return account_data[field]
            
            # If no combination found, try to construct one from account segments
            if 'BankAccountNumber' in account_data and account_data['BankAccountNumber']:
                # Use a default pattern based on account number
                account_num = str(account_data['BankAccountNumber'])
                # Create a simple combination pattern
                return f"3121-%-%-%-{account_num[-5:]}-%-%-%"
            
            return None
            
        except Exception as e:
            st.warning(f"Error extracting account combination from account: {e}")
            return None
    
    def search_cash_management_endpoints(self):
        """Search for Cash Management endpoints using different patterns"""
        try:
            st.info("🔍 Searching for Cash Management endpoints...")
            
            # Different API patterns to try
            api_patterns = [
                # Standard patterns
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagementCashBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagement",
                
                # Alternative patterns
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagementAccounts",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagementCashAccounts",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagementBankAccounts",
                
                # Treasury patterns
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/treasuryCashBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/treasuryManagement",
                
                # General ledger patterns
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/generalLedgerBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/ledgerBalances",
                
                # Different API versions
                f"{self.base_url}/fscmRestApi/resources/v1/cashManagementCashBalances",
                f"{self.base_url}/fscmRestApi/resources/latest/cashManagementCashBalances",
                f"{self.base_url}/fscmRestApi/resources/v1/cashBalances",
                f"{self.base_url}/fscmRestApi/resources/latest/cashBalances",
                
                # Alternative base paths
                f"{self.base_url}/restApi/resources/{self.api_version}/cashManagementCashBalances",
                f"{self.base_url}/restApi/resources/{self.api_version}/cashBalances",
                f"{self.base_url}/api/resources/{self.api_version}/cashManagementCashBalances",
                f"{self.base_url}/api/resources/{self.api_version}/cashBalances",
                
                # Different resource patterns
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagement/cashBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagement/balances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/treasury/cashBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/generalLedger/balances"
            ]
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            found_endpoints = []
            
            for endpoint in api_patterns:
                try:
                    st.info(f"🔍 Testing: {endpoint}")
                    response = self.session.get(endpoint, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Found working endpoint: {endpoint}")
                        data = response.json()
                        found_endpoints.append({
                            'endpoint': endpoint,
                            'data': data,
                            'structure': list(data.keys()) if isinstance(data, dict) else 'Array/List'
                        })
                    elif response.status_code == 401:
                        st.warning(f"⚠️ Requires auth: {endpoint}")
                    elif response.status_code == 403:
                        st.warning(f"⚠️ Forbidden: {endpoint}")
                    else:
                        st.warning(f"⚠️ Not available: {endpoint} ({response.status_code})")
                        
                except Exception as e:
                    st.warning(f"⚠️ Failed: {endpoint} - {str(e)[:50]}")
            
            if found_endpoints:
                st.success(f"✅ Found {len(found_endpoints)} working Cash Management endpoints!")
                for endpoint_info in found_endpoints:
                    st.info(f"💰 **Endpoint:** {endpoint_info['endpoint']}")
                    st.info(f"💰 **Structure:** {endpoint_info['structure']}")
                    if isinstance(endpoint_info['data'], dict) and 'items' in endpoint_info['data']:
                        st.info(f"💰 **Records:** {len(endpoint_info['data']['items'])}")
                        if endpoint_info['data']['items']:
                            sample = endpoint_info['data']['items'][0]
                            st.info(f"💰 **Sample fields:** {list(sample.keys())}")
                
                return found_endpoints
            else:
                st.warning("⚠️ No Cash Management endpoints found")
                return None
                
        except Exception as e:
            st.error(f"Failed to search Cash Management endpoints: {e}")
            return None
    
    def get_cash_management_balances(self):
        """Try to fetch Cash Management balances using the correct ledgerBalances endpoint"""
        try:
            # Use the official Oracle endpoint for ledger balances
            endpoint = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/ledgerBalances"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            st.info(f"🔍 Using official Oracle endpoint: {endpoint}")
            
            # First, try to get all ledger balances without filters
            response = self.session.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                st.success(f"✅ Found working ledger balances endpoint: {endpoint}")
                data = response.json()
                st.info(f"💰 **Ledger Balances Data Structure:** {list(data.keys()) if isinstance(data, dict) else 'List/Array'}")
                if isinstance(data, dict) and 'items' in data:
                    st.info(f"💰 **Number of Ledger Balance records:** {len(data['items'])}")
                    if data['items']:
                        sample_item = data['items'][0]
                        st.info(f"💰 **Sample fields:** {list(sample_item.keys())}")
                        
                        # Show balance-related fields
                        balance_fields = [key for key in sample_item.keys() if 'balance' in key.lower()]
                        if balance_fields:
                            st.info(f"💰 **Balance-related fields:** {balance_fields}")
                            for field in balance_fields:
                                if sample_item.get(field) is not None:
                                    st.info(f"💰 **{field}:** {sample_item[field]}")
                return data
            elif response.status_code == 401:
                st.warning(f"⚠️ Ledger balances endpoint requires auth: {endpoint}")
            elif response.status_code == 403:
                st.warning(f"⚠️ Ledger balances endpoint forbidden: {endpoint}")
            else:
                st.warning(f"⚠️ Ledger balances endpoint not available: {endpoint} ({response.status_code})")
                
        except Exception as e:
            st.error(f"Failed to fetch ledger balances: {e}")
            return None

    def get_account_balances_with_finder(self, account_combination=None, ledger_name=None, currency="USD", accounting_period=None):
        """Get account balances using the AccountBalanceFinder from official Oracle documentation"""
        try:
            endpoint = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/ledgerBalances"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Build query parameters for AccountBalanceFinder
            params = {
                'onlyData': 'true',
                'finder': 'AccountBalanceFinder',
                'fields': 'LedgerName,PeriodName,Currency,DetailAccountCombination,Scenario,BeginningBalance,PeriodActivity,EndingBalance,AmountType,CurrencyType'
            }
            
            # Add finder parameters if provided
            if account_combination:
                params['accountCombination'] = account_combination
            if ledger_name:
                params['ledgerName'] = ledger_name
            if currency:
                params['currency'] = currency
            if accounting_period:
                params['accountingPeriod'] = accounting_period
            
            response = self.session.get(endpoint, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'items' in data:
                    st.info(f"💰 **Number of Account Balance records:** {len(data['items'])}")
                    if data['items']:
                        for item in data['items']:
                            st.info(f"💰 **Account:** {item.get('DetailAccountCombination', 'N/A')}")
                            st.info(f"💰 **Beginning Balance:** {item.get('BeginningBalance', 'N/A')}")
                            st.info(f"💰 **Ending Balance:** {item.get('EndingBalance', 'N/A')}")
                            st.info(f"💰 **Period Activity:** {item.get('PeriodActivity', 'N/A')}")
                return data
            else:
                st.warning(f"⚠️ Account Balance Finder failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    st.info(f"🔍 Error details: {error_data}")
                except:
                    st.info(f"🔍 Error response: {response.text[:200]}")
                return None
                
        except Exception as e:
            st.error(f"Failed to fetch account balances with finder: {e}")
            return None
    
    def get_simple_ledger_balances(self):
        """Get ledger balances using a simple approach without finder"""
        try:
            endpoint = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/ledgerBalances"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Try simple GET request without complex parameters
            st.info(f"🔍 Trying simple ledger balances request: {endpoint}")
            
            response = self.session.get(endpoint, headers=headers, timeout=10)
            
            st.info(f"🔍 Response status: {response.status_code}")
            
            if response.status_code == 200:
                st.success("✅ Simple ledger balances request successful!")
                data = response.json()
                if isinstance(data, dict) and 'items' in data:
                    st.info(f"💰 **Number of Ledger Balance records:** {len(data['items'])}")
                    if data['items']:
                        sample_item = data['items'][0]
                        st.info(f"💰 **Sample fields:** {list(sample_item.keys())}")
                        
                        # Show balance-related fields
                        balance_fields = [key for key in sample_item.keys() if 'balance' in key.lower()]
                        if balance_fields:
                            st.info(f"💰 **Balance-related fields:** {balance_fields}")
                            for field in balance_fields:
                                if sample_item.get(field) is not None:
                                    st.info(f"💰 **{field}:** {sample_item[field]}")
                return data
            else:
                st.warning(f"⚠️ Simple ledger balances failed: {response.status_code}")
                try:
                    error_data = response.json()
                    st.info(f"🔍 Error details: {error_data}")
                except:
                    st.info(f"🔍 Error response: {response.text[:200]}")
                return None
                
        except Exception as e:
            st.error(f"Failed to fetch simple ledger balances: {e}")
            return None

    def get_real_opening_balances_bip(self):
        """Get real opening balances using BIP Publisher approach with working SQL"""
        try:
            # Use the exact same endpoint structure as the working client
            bip_endpoint = f"{self.base_url}:443/xmlpserver/services/v2/ReportService"
            
            # SQL query for latest opening balances per bank account (WORKING QUERY)
            sql_query = '''
            -- Get the LATEST opening balance for each bank account
            -- This ensures we only get the most recent balance when multiple records exist
            SELECT 
                'LATEST_OPENING_BALANCES' as source_type,
                bank_account_id,
                'OPBD' as balance_type,
                TO_CHAR(balance_date,'YYYY-MM-DD') as balance_date,
                balance_amount as opening_balance,
                TO_CHAR(LAST_UPDATE_DATE,'YYYY-MM-DD') as last_update_date
            FROM 
                CE_STMT_BALANCES ce1
            WHERE 
                balance_code = 'OPBD'
                AND balance_amount != 0
                -- Ensure we only get the record with the MAXIMUM balance_date for each account
                AND balance_date = (
                    SELECT MAX(balance_date) 
                    FROM CE_STMT_BALANCES ce2 
                    WHERE ce2.bank_account_id = ce1.bank_account_id 
                    AND ce2.balance_code = 'OPBD'
                    AND ce2.balance_amount != 0
                )
            ORDER BY 
                bank_account_id
            '''
            
            # Minify SQL like the working client
            minified_sql = sql_query.strip()
            minified_sql = re.sub(r'(--[^\n]*($|\n))|(/\*[\s\S]*?\*/)', '', minified_sql)
            minified_sql = re.sub(r'\s+', ' ', minified_sql)
            
            # Compress and encode the SQL query using the same method as the working client
            buf = BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb', mtime=0) as f:
                f.write(minified_sql.encode('utf-8'))
            encoded_sql = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            # Use the exact same SOAP structure as the working client
            soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v2="http://xmlns.oracle.com/oxp/service/v2">
   <soapenv:Header/>
   <soapenv:Body>
      <v2:runReport>
         <v2:reportRequest>
            <v2:reportAbsolutePath>/~cguidibi%40ca.ibm.com/_temp/wsq/csv.xdo</v2:reportAbsolutePath>
            <v2:attributeFormat>csv</v2:attributeFormat>
            <v2:sizeOfDataChunkDownload>-1</v2:sizeOfDataChunkDownload>
            <v2:parameterNameValues>
               <v2:listOfParamNameValues>
                  <v2:item>
                     <v2:name>P_B64_CONTENT</v2:name>
                     <v2:values>
                        <v2:item>{encoded_sql}</v2:item>
                     </v2:values>
                  </v2:item>
               </v2:listOfParamNameValues>
            </v2:parameterNameValues>
         </v2:reportRequest>
         <v2:userID>{st.session_state.username}</v2:userID>
         <v2:password>{st.session_state.password}</v2:password>
      </v2:runReport>
   </soapenv:Body>
</soapenv:Envelope>'''
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'runReport'
            }
            
            response = self.session.post(bip_endpoint, data=soap_request.encode('utf-8'), headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Parse SOAP response using the correct namespace
                root = ET.fromstring(response.text)
                namespaces = {
                    'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                    'v2': 'http://xmlns.oracle.com/oxp/service/v2'
                }
                
                # Extract data from SOAP response
                try:
                    # Look for report data in the response
                    report_data = root.find('.//v2:reportBytes', namespaces)
                    if report_data is not None and report_data.text:
                        # Decode and parse the report data
                        decoded_data = base64.b64decode(report_data.text)
                        
                        # Try to parse as CSV
                        try:
                            df = pd.read_csv(BytesIO(decoded_data), delimiter='|', encoding='utf-8', dtype=str)
                            df = df.dropna(axis=1, how="all")
                            df = df.fillna('')
                            
                            st.success("✅ Real opening balances fetched successfully via BIP Publisher!")
                            st.info(f"💰 Found {len(df)} balance records")
                            st.dataframe(df.head(), use_container_width=True)
                            return {"status": "success", "message": f"Found {len(df)} balance records", "data": df}
                        except Exception as csv_error:
                            st.warning(f"⚠️ Could not parse CSV data: {csv_error}")
                            return {"status": "success", "message": "Raw data received from BIP Publisher"}
                    else:
                        st.warning("⚠️ No report data found in BIP response")
                        return None
                except Exception as parse_error:
                    st.warning(f"⚠️ Error parsing BIP response: {parse_error}")
                    return None
            else:
                st.warning(f"⚠️ BIP Publisher request failed with status {response.status_code}")
                
                # Try alternative BIP endpoints with the correct structure
                alternative_endpoints = [
                    f"{self.base_url}:443/xmlpserver/services/v2/PublicReportService",
                    f"{self.base_url}:443/xmlpserver/services/v11/PublicReportService",
                    f"{self.base_url}:443/xmlpserver/services/v2/ReportService"
                ]
                
                for alt_endpoint in alternative_endpoints:
                    try:
                        alt_response = self.session.post(alt_endpoint, data=soap_request.encode('utf-8'), headers=headers, timeout=10)
                        if alt_response.status_code == 200:
                            st.success(f"✅ Found working BIP endpoint: {alt_endpoint}")
                            return {"status": "success", "message": f"Found working endpoint: {alt_endpoint}"}
                    except Exception as e:
                        st.warning(f"⚠️ Alternative endpoint failed: {e}")
                
                return None
                
        except Exception as e:
            st.error(f"Failed to fetch real opening balances via BIP: {e}")
            st.info("🔍 **Troubleshooting Tips:**")
            st.info("• Check if BIP Publisher is enabled in your Oracle Fusion instance")
            st.info("• Verify the report file 'wsq.xdrz' is uploaded to /Temp/ folder")
            st.info("• Check if you have BIP Publisher permissions")
            st.info("• Try using the REST API approach instead")
            return None

    def get_real_opening_balances_rest(self):
        """Get real opening balances using REST API approach (fallback when BIP fails)"""
        try:
            st.info("🔍 Trying REST API approach for opening balances...")
            
            # Try different REST endpoints for balance data
            rest_endpoints = [
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/ledgerBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashManagementCashBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashBalances",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/bankAccounts"
            ]
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            for endpoint in rest_endpoints:
                try:
                    st.info(f"🔍 Trying REST endpoint: {endpoint}")
                    response = self.session.get(endpoint, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ Found working REST endpoint: {endpoint}")
                        
                        if isinstance(data, dict) and 'items' in data and data['items']:
                            st.info(f"💰 Found {len(data['items'])} balance records")
                            
                            # Show sample data structure
                            sample_item = data['items'][0]
                            st.info(f"💰 **Sample fields:** {list(sample_item.keys())}")
                            
                            # Look for balance-related fields
                            balance_fields = [key for key in sample_item.keys() if 'balance' in key.lower() or 'amount' in key.lower()]
                            if balance_fields:
                                st.info(f"💰 **Balance-related fields:** {balance_fields}")
                                for field in balance_fields:
                                    if sample_item.get(field) is not None:
                                        st.info(f"💰 **{field}:** {sample_item[field]}")
                            
                            return {
                                "status": "success", 
                                "message": f"Found {len(data['items'])} balance records via REST API",
                                "data": data
                            }
                        else:
                            st.warning(f"⚠️ No data found in {endpoint}")
                    else:
                        st.warning(f"⚠️ {endpoint} returned status {response.status_code}")
                        
                except Exception as e:
                    st.warning(f"⚠️ {endpoint} failed: {e}")
            
            st.error("❌ No working REST endpoints found for balance data")
            return None
            
        except Exception as e:
            st.error(f"Failed to fetch opening balances via REST API: {e}")
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
    
    def discover_available_endpoints(self):
        """Discover available endpoints in the Oracle Fusion instance"""
        st.info("🔍 Discovering available endpoints...")
        
        # Common endpoints to test
        endpoints_to_test = [
            "cashBankAccounts",
            "bankStatements", 
            "externalCashTransactions",
            "apInvoices",
            "arInvoices",
            "glJournals",
            "generalLedgerJournals",
            "journals",
            "glJournalEntries",
            "bankStatementImport",
            "cashBankStatements"
        ]
        
        available_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                test_url = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/{endpoint}"
                response = self.session.get(test_url, timeout=5)
                
                if response.status_code == 200:
                    st.success(f"✅ {endpoint} - Available")
                    available_endpoints.append(endpoint)
                elif response.status_code == 401:
                    st.warning(f"⚠️ {endpoint} - Requires authentication")
                    available_endpoints.append(f"{endpoint} (auth required)")
                elif response.status_code == 403:
                    st.warning(f"⚠️ {endpoint} - Access forbidden")
                elif response.status_code == 404:
                    st.info(f"❌ {endpoint} - Not found")
                else:
                    st.info(f"ℹ️ {endpoint} - Status {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ {endpoint} - Error: {e}")
        
        return available_endpoints

    # ===== POSTING METHODS =====
    def post_bank_statement(self, bai2_data):
        """Post BAI2 bank statement to Oracle Fusion"""
        try:
            # Try different possible endpoints for bank statements
            possible_endpoints = [
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/bankStatements",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/bankStatementImport",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashBankStatements"
            ]
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Convert BAI2 data to Oracle Fusion format
            fusion_data = self._convert_bai2_to_fusion_format(bai2_data)
            
            st.info(f"📤 Posting bank statement")
            
            # Try each endpoint until one works
            for i, api_url in enumerate(possible_endpoints):
                st.info(f"🔍 Trying endpoint {i+1}: {api_url}")
                response = self.session.post(api_url, headers=headers, json=fusion_data, timeout=self.timeout)
                
                if response.status_code in [200, 201]:
                    st.success(f"✅ Found working endpoint: {api_url}")
                    return self._handle_posting_response(response, "Bank Statement")
                elif response.status_code == 404:
                    st.warning(f"⚠️ Endpoint not found: {api_url}")
                    continue
                else:
                    return self._handle_posting_response(response, "Bank Statement")
            
            # If all endpoints fail
            st.error("❌ All bank statement endpoints returned 404. Bank statement posting may not be available in this Oracle Fusion instance.")
            return False
            
        except Exception as e:
            st.error(f"❌ Failed to post bank statement: {e}")
            return False
    
    def post_external_cash_transactions(self, transactions):
        """Post external cash transactions to Oracle Fusion"""
        try:
            api_url = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/externalCashTransactions"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Convert to Oracle Fusion format
            fusion_data = self._convert_external_cash_to_fusion_format(transactions)
            
            st.info(f"📤 Posting {len(transactions)} external cash transactions")
            response = self.session.post(api_url, headers=headers, json=fusion_data, timeout=self.timeout)
            
            return self._handle_posting_response(response, "External Cash Transactions")
            
        except Exception as e:
            st.error(f"❌ Failed to post external cash transactions: {e}")
            return False
    
    def post_ap_invoices(self, invoices):
        """Post AP invoices to Oracle Fusion"""
        try:
            api_url = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/apInvoices"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Convert to Oracle Fusion format
            fusion_data = self._convert_ap_invoices_to_fusion_format(invoices)
            
            st.info(f"📤 Posting {len(invoices)} AP invoices")
            response = self.session.post(api_url, headers=headers, json=fusion_data, timeout=self.timeout)
            
            return self._handle_posting_response(response, "AP Invoices")
            
        except Exception as e:
            st.error(f"❌ Failed to post AP invoices: {e}")
            return False
    
    def post_ar_invoices(self, invoices):
        """Post AR invoices to Oracle Fusion"""
        try:
            api_url = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/arInvoices"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Convert to Oracle Fusion format
            fusion_data = self._convert_ar_invoices_to_fusion_format(invoices)
            
            st.info(f"📤 Posting {len(invoices)} AR invoices")
            response = self.session.post(api_url, headers=headers, json=fusion_data, timeout=self.timeout)
            
            return self._handle_posting_response(response, "AR Invoices")
            
        except Exception as e:
            st.error(f"❌ Failed to post AR invoices: {e}")
            return False
    
    def post_gl_journals(self, journals):
        """Post GL journals to Oracle Fusion"""
        try:
            # Try different possible endpoints for GL journals
            possible_endpoints = [
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/glJournals",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/generalLedgerJournals",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/journals",
                f"{self.base_url}/fscmRestApi/resources/{self.api_version}/glJournalEntries"
            ]
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Convert to Oracle Fusion format
            fusion_data = self._convert_gl_journals_to_fusion_format(journals)
            
            st.info(f"📤 Posting {len(journals)} GL journals")
            
            # Try each endpoint until one works
            for i, api_url in enumerate(possible_endpoints):
                st.info(f"🔍 Trying endpoint {i+1}: {api_url}")
                response = self.session.post(api_url, headers=headers, json=fusion_data, timeout=self.timeout)
                
                if response.status_code in [200, 201]:
                    st.success(f"✅ Found working endpoint: {api_url}")
                    return self._handle_posting_response(response, "GL Journals")
                elif response.status_code == 404:
                    st.warning(f"⚠️ Endpoint not found: {api_url}")
                    continue
                else:
                    return self._handle_posting_response(response, "GL Journals")
            
            # If all endpoints fail
            st.error("❌ All GL journal endpoints returned 404. GL journal posting may not be available in this Oracle Fusion instance.")
            st.info("💡 **Available endpoints in your instance:**")
            st.info("• Bank Accounts: /cashBankAccounts ✅")
            st.info("• Other endpoints may need to be discovered")
            return False
            
        except Exception as e:
            st.error(f"❌ Failed to post GL journals: {e}")
            return False
    
    def _handle_posting_response(self, response, data_type):
        """Handle posting response and show appropriate messages"""
        if response.status_code == 200 or response.status_code == 201:
            st.success(f"✅ Successfully posted {data_type} to Oracle Fusion!")
            try:
                result = response.json()
                st.info(f"📊 Response: {result.get('status', 'Success')}")
                return True
            except:
                st.info("📊 Posted successfully")
                return True
        elif response.status_code == 401:
            st.error("❌ Authentication required for posting")
            return False
        elif response.status_code == 403:
            st.error("❌ Access forbidden - check posting permissions")
            return False
        elif response.status_code == 400:
            st.error(f"❌ Bad request - check data format")
            try:
                error_details = response.json()
                st.error(f"Error details: {error_details}")
            except:
                pass
            return False
        else:
            st.error(f"❌ Posting failed with status {response.status_code}")
            return False
    
    # ===== DATA CONVERSION METHODS =====
    
    def _convert_bai2_to_fusion_format(self, bai2_data):
        """Convert BAI2 data to Oracle Fusion format"""
        # This is a simplified conversion - actual format depends on Oracle Fusion API
        return {
            "bankStatementData": bai2_data,
            "source": "Demo Transaction Generator",
            "importDate": pd.Timestamp.now().isoformat()
        }
    
    def _convert_external_cash_to_fusion_format(self, transactions):
        """Convert external cash transactions to Oracle Fusion format"""
        fusion_transactions = []
        for transaction in transactions:
            fusion_transaction = {
                "bankAccountName": transaction.get('BankAccountName'),
                "amount": transaction.get('Amount'),
                "transactionDate": transaction.get('TransactionDate'),
                "transactionType": transaction.get('TransactionType'),
                "reference": transaction.get('Reference'),
                "businessUnit": transaction.get('BusinessUnit'),
                "reconciled": transaction.get('Reconciled') == 'Y',
                "source": "Demo Transaction Generator"
            }
            fusion_transactions.append(fusion_transaction)
        
        return {
            "transactions": fusion_transactions,
            "source": "Demo Transaction Generator"
        }
    
    def _convert_ap_invoices_to_fusion_format(self, invoices):
        """Convert AP invoices to Oracle Fusion format"""
        fusion_invoices = []
        for invoice in invoices:
            header = invoice['header']
            lines = invoice['lines']
            
            fusion_invoice = {
                "invoiceId": header.get('InvoiceId'),
                "invoiceNumber": header.get('InvoiceNumber'),
                "invoiceDate": header.get('InvoiceDate'),
                "dueDate": header.get('DueDate'),
                "invoiceType": header.get('InvoiceType'),
                "businessUnit": header.get('BusinessUnit'),
                "currency": header.get('Currency'),
                "supplierName": header.get('SupplierName'),
                "supplierNumber": header.get('SupplierNumber'),
                "invoiceAmount": header.get('InvoiceAmount'),
                "status": header.get('Status'),
                "description": header.get('Description'),
                "lines": []
            }
            
            for line in lines:
                fusion_line = {
                    "lineNumber": line.get('LineNumber'),
                    "lineType": line.get('LineType'),
                    "amount": line.get('Amount'),
                    "quantity": line.get('Quantity'),
                    "unitPrice": line.get('UnitPrice'),
                    "description": line.get('Description'),
                    "expenseCategory": line.get('ExpenseCategory'),
                    "glAccount": line.get('GLAccount'),
                    "taxCode": line.get('TaxCode'),
                    "lineStatus": line.get('LineStatus')
                }
                fusion_invoice["lines"].append(fusion_line)
            
            fusion_invoices.append(fusion_invoice)
        
        return {
            "invoices": fusion_invoices,
            "source": "Demo Transaction Generator"
        }
    
    def _convert_ar_invoices_to_fusion_format(self, invoices):
        """Convert AR invoices to Oracle Fusion format"""
        fusion_invoices = []
        for invoice in invoices:
            header = invoice['header']
            lines = invoice['lines']
            
            fusion_invoice = {
                "invoiceId": header.get('InvoiceId'),
                "invoiceNumber": header.get('InvoiceNumber'),
                "invoiceDate": header.get('InvoiceDate'),
                "dueDate": header.get('DueDate'),
                "invoiceType": header.get('InvoiceType'),
                "businessUnit": header.get('BusinessUnit'),
                "currency": header.get('Currency'),
                "customerName": header.get('CustomerName'),
                "customerNumber": header.get('CustomerNumber'),
                "invoiceAmount": header.get('InvoiceAmount'),
                "status": header.get('Status'),
                "paymentTerms": header.get('PaymentTerms'),
                "description": header.get('Description'),
                "lines": []
            }
            
            for line in lines:
                fusion_line = {
                    "lineNumber": line.get('LineNumber'),
                    "lineType": line.get('LineType'),
                    "amount": line.get('Amount'),
                    "quantity": line.get('Quantity'),
                    "unitPrice": line.get('UnitPrice'),
                    "description": line.get('Description'),
                    "revenueCategory": line.get('RevenueCategory'),
                    "glAccount": line.get('GLAccount'),
                    "taxCode": line.get('TaxCode'),
                    "lineStatus": line.get('LineStatus')
                }
                fusion_invoice["lines"].append(fusion_line)
            
            fusion_invoices.append(fusion_invoice)
        
        return {
            "invoices": fusion_invoices,
            "source": "Demo Transaction Generator"
        }
    
    def _convert_gl_journals_to_fusion_format(self, journals):
        """Convert GL journals to Oracle Fusion format"""
        fusion_journals = []
        for journal in journals:
            header = journal['header']
            lines = journal['lines']
            
            fusion_journal = {
                "journalId": header.get('JournalId'),
                "journalName": header.get('JournalName'),
                "journalDate": header.get('JournalDate'),
                "journalType": header.get('JournalType'),
                "businessUnit": header.get('BusinessUnit'),
                "ledger": header.get('Ledger'),
                "currency": header.get('Currency'),
                "journalSource": header.get('JournalSource'),
                "journalCategory": header.get('JournalCategory'),
                "periodName": header.get('PeriodName'),
                "status": header.get('Status'),
                "description": header.get('Description'),
                "totalDebit": header.get('TotalDebit'),
                "totalCredit": header.get('TotalCredit'),
                "lines": []
            }
            
            for line in lines:
                fusion_line = {
                    "lineNumber": line.get('LineNumber'),
                    "accountType": line.get('AccountType'),
                    "glAccount": line.get('GLAccount'),
                    "description": line.get('Description'),
                    "debitAmount": line.get('DebitAmount'),
                    "creditAmount": line.get('CreditAmount'),
                    "lineType": line.get('LineType'),
                    "currency": line.get('Currency'),
                    "businessUnit": line.get('BusinessUnit'),
                    "ledger": line.get('Ledger'),
                    "periodName": line.get('PeriodName'),
                    "status": line.get('Status')
                }
                fusion_journal["lines"].append(fusion_line)
            
            fusion_journals.append(fusion_journal)
        
        return {
            "journals": fusion_journals,
            "source": "Demo Transaction Generator"
        }

    def get_simple_opening_balances(self):
        """Get opening balances using the bank accounts endpoint that we know works"""
        try:
            st.info("🔍 Getting opening balances from bank accounts data...")
            
            # Use the bank accounts endpoint that we know works
            api_url = f"{self.base_url}/fscmRestApi/resources/{self.api_version}/cashBankAccounts"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            params = {
                'limit': 50,  # Get more accounts
                'onlyData': 'true'
            }
            
            response = self.session.get(api_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and data['items']:
                    st.success(f"✅ Found {len(data['items'])} bank accounts")
                    
                    # Extract opening balances from bank account data
                    opening_balances = []
                    for account in data['items']:
                        account_id = account.get('BankAccountId')
                        account_name = account.get('BankAccountName', 'Unknown')
                        account_number = account.get('BankAccountNumber', 'Unknown')
                        currency = account.get('CurrencyCode', 'USD')
                        
                        # Try to extract balance from account data
                        opening_balance = 0.0
                        balance_field = "No balance found"
                        
                        # Check for balance fields in account data
                        balance_fields = [
                            'OpeningBalance', 'CurrentBalance', 'Balance', 'AccountBalance',
                            'LedgerBalance', 'BookBalance', 'AvailableBalance', 'RunningBalance',
                            'CashBalance', 'CashManagementBalance', 'CashManagementCashBalance'
                        ]
                        
                        for field in balance_fields:
                            if field in account and account[field] is not None:
                                try:
                                    balance = float(account[field])
                                    if balance != 0:
                                        opening_balance = balance
                                        balance_field = field
                                        break
                                except (ValueError, TypeError):
                                    continue
                        
                        # If no balance found, try nested objects
                        if opening_balance == 0.0:
                            nested_objects = ['Balance', 'CashManagement', 'CashBalance']
                            for obj_name in nested_objects:
                                if obj_name in account and isinstance(account[obj_name], dict):
                                    for field in balance_fields:
                                        if field in account[obj_name] and account[obj_name][field] is not None:
                                            try:
                                                balance = float(account[obj_name][field])
                                                if balance != 0:
                                                    opening_balance = balance
                                                    balance_field = f"{obj_name}.{field}"
                                                    break
                                            except (ValueError, TypeError):
                                                continue
                        
                        opening_balances.append({
                            'bank_account_id': account_id,
                            'account_name': account_name,
                            'account_number': account_number,
                            'currency': currency,
                            'opening_balance': opening_balance,
                            'balance_field': balance_field
                        })
                    
                    # Show results
                    st.info(f"💰 **Opening Balances Found:**")
                    for balance in opening_balances:
                        if balance['opening_balance'] > 0:
                            st.info(f"• {balance['account_name']}: {balance['opening_balance']:,.2f} {balance['currency']} (from {balance['balance_field']})")
                    
                    return {
                        "status": "success",
                        "message": f"Found {len(opening_balances)} bank accounts with balance data",
                        "data": opening_balances
                    }
                else:
                    st.warning("⚠️ No bank accounts found")
                    return None
            else:
                st.warning(f"⚠️ Bank accounts endpoint returned status {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Failed to get opening balances: {e}")
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
    
    # Authentication section
    st.subheader("🔐 Authentication")
    username = st.text_input("Username", value=st.session_state.username, help="Your Oracle Fusion username", key="username_input")
    password = st.text_input("Password", value=st.session_state.password, type="password", help="Your Oracle Fusion password", key="password_input")
    
    # Store credentials in session state
    if username != st.session_state.username:
        st.session_state.username = username
    if password != st.session_state.password:
        st.session_state.password = password
    
    # Oracle connection test - SIMPLIFIED
    st.subheader("Oracle Connection")
    if st.button("Test Oracle Connection", key="test_connection_btn"):
        try:
            client = SimpleOracleClient(config)
            # Add authentication if provided
            if username and password:
                client.session.auth = (username, password)
            
            result = client.get_bank_accounts_simple()
            if result and 'items' in result and len(result['items']) > 0:
                st.success("✅ Connected successfully!")
            else:
                st.error("❌ Connection failed - No accounts found")
        except Exception as e:
            st.error(f"❌ Connection failed due to: {str(e)}")
    
    # Test Real Opening Balances
    st.subheader("💰 Test Real Opening Balances")
    st.info("💡 **This fetches real opening balances from your Oracle Fusion instance**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Test Simple Bank Accounts", key="test_simple_btn"):
            try:
                client = SimpleOracleClient(config)
                # Add authentication if provided
                if username and password:
                    client.session.auth = (username, password)
                
                # Try the simple bank accounts approach (we know it works)
                simple_result = client.get_simple_opening_balances()
                
                if simple_result and 'data' in simple_result:
                    st.success("✅ Simple bank accounts working!")
                    st.session_state.simple_opening_balances = simple_result
                    
                    # Show simple table instead of verbose messages
                    st.subheader("📊 Simple Bank Accounts")
                    balances_df = pd.DataFrame(simple_result['data'])
                    st.dataframe(balances_df, use_container_width=True)
                    
                    # Show summary
                    non_zero_balances = [b for b in simple_result['data'] if b['opening_balance'] > 0]
                    st.info(f"💰 Found {len(non_zero_balances)} accounts with non-zero balances")
                else:
                    st.error("❌ Failed to fetch opening balances")
            except Exception as e:
                st.error(f"❌ Error testing opening balances: {e}")
    
    with col2:
        if st.button("🔍 Test BIP Publisher", key="test_bip_btn"):
            try:
                client = SimpleOracleClient(config)
                # Add authentication if provided
                if username and password:
                    client.session.auth = (username, password)
                
                # Try the BIP Publisher approach with working SQL
                bip_result = client.get_real_opening_balances_bip()
                
                if bip_result and 'data' in bip_result:
                    st.success("✅ BIP Publisher working!")
                    st.session_state.bip_opening_balances = bip_result
                    
                    # Show simple table instead of verbose messages
                    if hasattr(bip_result['data'], 'head'):
                        st.subheader("📊 BIP Opening Balances")
                        st.dataframe(bip_result['data'], use_container_width=True)
                        
                        # Show summary
                        total_records = len(bip_result['data'])
                        st.info(f"💰 Found {total_records} opening balance records")
                else:
                    st.warning("⚠️ BIP Publisher failed - report file may not exist")
            except Exception as e:
                st.error(f"❌ Error testing BIP Publisher: {e}")

# Main content
tab1, tab2 = st.tabs([
    "💰 Real Balances", 
    "💳 Transactions"
])

with tab1:
    st.success("🎯 **REAL BALANCES - ORACLE FUSION**")
    st.markdown("Fetch real opening balances per account per day")
    
    # Input parameters
    transactions_per_account = st.number_input(
        "Transactions per Account",
        min_value=1,
        max_value=100,
        value=st.session_state.transactions_per_account,
        help="Number of transactions to generate per bank account",
        key="transactions_per_account_tab1"
    )
    
    # Add target closing balance input
    st.subheader("💰 Target Closing Balances")
    st.info("💡 **Set target closing balances for each account (optional)**")
    
    # Create a simple interface for setting target closing balances
    target_balances = {}
    for account in st.session_state.real_accounts:
        opening_balance = account['opening_balance']
        
        # Calculate default target based on opening balance
        if opening_balance >= 0:
            default_target = opening_balance * 1.1  # 10% increase for positive balances
        else:
            default_target = opening_balance * 0.9  # 10% decrease for negative balances (closer to zero)
        
        # Set dynamic min_value based on opening balance
        if opening_balance >= 0:
            min_value = 0.0
        else:
            min_value = opening_balance * 2  # Allow up to 2x the negative balance
        
        target_balance = st.number_input(
            f"Target Closing Balance for {account['account_name']}",
            min_value=min_value,
            value=default_target,
            step=abs(opening_balance) * 0.01,  # Dynamic step size
            format="%.2f",
            help=f"Current opening balance: {opening_balance:,.2f} {account['currency']}",
            key=f"target_balance_{account['account_id']}"
        )
        target_balances[account['account_id']] = target_balance
    
    # Fetch button
    if st.button("Fetch Real Bank Accounts", type="primary", key="fetch_accounts_btn"):
        try:
            client = SimpleOracleClient(config)
            
            # Add authentication if provided in sidebar
            if 'username' in st.session_state and 'password' in st.session_state:
                if st.session_state.username and st.session_state.password:
                    client.session.auth = (st.session_state.username, st.session_state.password)
            
            result = client.get_bank_accounts_simple()
            bip_opening_balances = client.get_real_opening_balances_bip()
            
            if result and 'items' in result:
                # Store the complete raw API response
                st.session_state.raw_api_response = result
                
                # Store BIP opening balances data if available
                if bip_opening_balances:
                    st.session_state.bip_opening_balances = bip_opening_balances
                    # Show BIP balance summary
                    if 'data' in bip_opening_balances and hasattr(bip_opening_balances['data'], '__len__'):
                        bip_count = len(bip_opening_balances['data'])
                        st.info(f"💰 BIP Opening Balances: Found {bip_count} records")
                    else:
                        st.info("💰 BIP Opening Balances: Data available")
                
                # Process real accounts for display with opening balances
                processed_accounts = []
                for account in result['items']:
                    account_id = account.get('BankAccountId')
                    account_name = account.get('BankAccountName', 'Unknown')
                    account_number = account.get('BankAccountNumber', '')
                    
                    # Extract account combination for balance lookup
                    account_combination = client.extract_account_combination_from_bank_account(account)
                    
                    # Use the new balance extraction method
                    opening_balance, balance_field = client.extract_balance_from_bank_account(account)
                    
                    # If no balance found in account data, try to get it from BIP opening balances
                    if opening_balance == 0.0 and bip_opening_balances and 'data' in bip_opening_balances:
                        try:
                            # Look for matching account in BIP opening balances data
                            bip_data = bip_opening_balances['data']
                            if hasattr(bip_data, 'to_dict'):
                                # Convert DataFrame to list of dicts if needed
                                bip_records = bip_data.to_dict('records')
                            else:
                                bip_records = bip_data
                            
                            account_id = account.get('BankAccountId')
                            for bip_record in bip_records:
                                # Try both uppercase and lowercase column names
                                bip_account_id = str(bip_record.get('BANK_ACCOUNT_ID', bip_record.get('bank_account_id', '')))
                                bip_balance = float(bip_record.get('OPENING_BALANCE', bip_record.get('opening_balance', 0)))
                                
                                if str(account_id) == bip_account_id:
                                    if bip_balance != 0:  # Changed from > 0 to != 0 to include negative balances
                                        opening_balance = bip_balance
                                        break
                        except Exception as e:
                            pass
                    
                    # Try to get from BIP opening balances first
                    if bip_opening_balances and 'data' in bip_opening_balances:
                        try:
                            bip_data = bip_opening_balances['data']
                            if hasattr(bip_data, 'to_dict'):
                                bip_records = bip_data.to_dict('records')
                            else:
                                bip_records = bip_data
                            
                            account_id = account.get('BankAccountId')
                            account_number = account.get('BankAccountNumber', '')
                            
                            # Try multiple matching strategies
                            for bip_record in bip_records:
                                # Try both uppercase and lowercase column names
                                bip_account_id = str(bip_record.get('BANK_ACCOUNT_ID', bip_record.get('bank_account_id', '')))
                                bip_balance = float(bip_record.get('OPENING_BALANCE', bip_record.get('opening_balance', 0)))
                                
                                # Match by account ID or account number
                                if (str(account_id) == bip_account_id or 
                                    str(account_number) == bip_account_id or
                                    account_number in bip_account_id or
                                    bip_account_id in account_number):
                                    if bip_balance != 0:  # Changed from > 0 to != 0 to include negative balances
                                        opening_balance = bip_balance
                                        break
                        except Exception as e:
                            pass
                    
                    # If still no balance found, use default value
                    if opening_balance == 0.0:
                        opening_balance = 10000.0  # Default opening balance
                    
                    processed_account = {
                        'account_id': str(account.get('BankAccountId', 'Unknown')),
                        'account_name': account.get('BankAccountName', 'Unknown Account'),
                        'account_number': account.get('BankAccountNumber', ''),
                        'bank_name': account.get('BankName', 'Unknown Bank'),
                        'currency': account.get('CurrencyCode', 'USD'),
                        'account_number_for_transactions': account.get('BankAccountNumber', ''),
                        'opening_balance': opening_balance,
                        'closing_balance': opening_balance,  # Default to opening balance initially
                        'account_combination': account_combination  # Store for future use
                    }
                    processed_accounts.append(processed_account)
                    
                    # No verbose messages - clean interface
                
                st.session_state.real_accounts = processed_accounts
                st.session_state.transactions_per_account = transactions_per_account
                
                st.success(f"✅ Fetched {len(processed_accounts)} real bank accounts!")
                
                # Show simple table instead of verbose messages
                st.subheader("📊 Bank Accounts Summary")
                summary_data = []
                for acc in processed_accounts:
                    summary_data.append({
                        'Account Name': acc['account_name'],
                        'Account Number': acc['account_number'],
                        'Bank': acc['bank_name'],
                        'Currency': acc['currency'],
                        'Opening Balance': f"{acc['opening_balance']:,.2f}"
                    })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
                
            else:
                st.error("❌ No accounts found or API error")
                
        except Exception as e:
            st.error(f"❌ Error fetching accounts: {e}")
            # Fallback to fake data
            fake_accounts = [
                {
                    'account_id': '300000004068939',
                    'account_name': 'Main Operating Account',
                    'account_number': '1234567890',
                    'bank_name': 'Test Bank',
                    'currency': 'USD',
                    'account_number_for_transactions': '1234567890',
                    'opening_balance': 50000.0,
                    'closing_balance': 50000.0
                },
                {
                    'account_id': '300000004068940',
                    'account_name': 'Secondary Account',
                    'account_number': '0987654321',
                    'bank_name': 'Test Bank 2',
                    'currency': 'USD',
                    'account_number_for_transactions': '0987654321',
                    'opening_balance': 25000.0,
                    'closing_balance': 25000.0
                }
            ]
            st.session_state.real_accounts = fake_accounts
            st.session_state.transactions_per_account = transactions_per_account
            st.success(f"✅ Using {len(fake_accounts)} demo accounts!")
    
    # Display real balances table
    if st.session_state.real_accounts:
        st.subheader("💰 Real Opening Balances")
        
        # Simple table showing real balances per account
        balance_data = []
        for account in st.session_state.real_accounts:
            balance_data.append({
                'Account Name': account['account_name'],
                'Account Number': account['account_number'],
                'Bank': account['bank_name'],
                'Currency': account['currency'],
                'Opening Balance': f"{account['opening_balance']:,.2f}",
                'Balance Date': '2025-01-15'  # Default date
            })
        
        balance_df = pd.DataFrame(balance_data)
        st.dataframe(balance_df, use_container_width=True)
        
        # Download complete raw API response (simplified - no preview)
        if 'raw_api_response' in st.session_state:
            import json
            raw_json_data = json.dumps(st.session_state.raw_api_response, indent=2)
            st.download_button(
                label="📥 Download Complete Raw JSON",
                data=raw_json_data,
                file_name="oracle_bank_accounts_complete.json",
                mime="application/json"
            )
        
        # Generate transactions button with balance logic
        if st.button("Generate Demo Transactions", type="primary", key="generate_transactions_btn"):
            st.info("🔄 Generating transactions with balance logic...")
            
            # Generate transactions that respect the balance logic
            all_transactions = []
            for account in st.session_state.real_accounts:
                opening_bal = account['opening_balance']
                # Use target balance from input, or default to opening balance if not set
                target_balance = target_balances.get(account['account_id'], opening_bal)
                required_change = target_balance - opening_bal
                
                # Calculate transactions to achieve the required change
                transactions = []
                remaining_change = required_change
                
                for i in range(st.session_state.transactions_per_account):
                    if i == st.session_state.transactions_per_account - 1:
                        # Last transaction - use remaining amount to balance exactly
                        amount = remaining_change
                    else:
                        # Generate meaningful transaction amounts
                        # Use a percentage of the required change for each transaction
                        transaction_percentage = 0.8 / (st.session_state.transactions_per_account - 1)  # 80% of change distributed
                        base_amount = abs(required_change) * transaction_percentage
                        
                        # Add some variation and alternate between positive/negative
                        variation = base_amount * 0.3 * (1 if i % 2 == 0 else -1)
                        amount = base_amount + variation
                        
                        # Ensure we don't exceed the remaining change
                        if remaining_change > 0:
                            amount = min(amount, remaining_change)
                        else:
                            amount = max(amount, remaining_change)
                        
                        # For very small amounts, create minimum meaningful transactions
                        if abs(amount) < 0.01:
                            amount = 100.0 if remaining_change > 0 else -100.0
                        
                        # Round to 2 decimal places
                        amount = round(amount, 2)
                    
                    # Calculate running balance
                    current_balance = opening_bal
                    for prev_txn in transactions:
                        if prev_txn['type'] == 'Credit':
                            current_balance += prev_txn['amount']
                        else:
                            current_balance -= prev_txn['amount']
                    
                    # Add current transaction to running balance
                    if amount > 0:
                        current_balance += amount
                    else:
                        current_balance -= abs(amount)
                    
                    transaction = {
                        'account_id': account['account_id'],
                        'account_name': account['account_name'],
                        'transaction_id': f"TXN{i+1:03d}",
                        'date': f"2024-01-{(i+1):02d}",
                        'description': f"Demo transaction {i+1}",
                        'amount': abs(amount),
                        'type': 'Credit' if amount > 0 else 'Debit',
                        'running_balance': current_balance
                    }
                    transactions.append(transaction)
                    remaining_change -= amount
                
                all_transactions.extend(transactions)
            
            # Display transactions
            st.subheader("📊 Generated Transactions (Balanced)")
            transactions_df = pd.DataFrame(all_transactions)
            st.dataframe(transactions_df, use_container_width=True)
            
            # Show balance verification
            st.subheader("💰 Balance Verification")
            for account in st.session_state.real_accounts:
                account_transactions = [t for t in all_transactions if t['account_id'] == account['account_id']]
                total_credits = sum(t['amount'] for t in account_transactions if t['type'] == 'Credit')
                total_debits = sum(t['amount'] for t in account_transactions if t['type'] == 'Debit')
                net_change = total_credits - total_debits
                final_balance = account['opening_balance'] + net_change
                target_balance = target_balances.get(account['account_id'], account['opening_balance'])
                
                st.write(f"**{account['account_name']}:**")
                st.write(f"  Opening: {account['opening_balance']:,.2f} {account['currency']}")
                st.write(f"  Credits: +{total_credits:,.2f} | Debits: -{total_debits:,.2f}")
                st.write(f"  Net Change: {net_change:+,.2f}")
                st.write(f"  Final Balance: {final_balance:,.2f} {account['currency']}")
                st.write(f"  Target: {target_balance:,.2f} {account['currency']}")
                
                # Show if target was achieved
                if abs(final_balance - target_balance) < 0.01:
                    st.success(f"  ✅ Target achieved!")
                else:
                    st.warning(f"  ⚠️ Target difference: {final_balance - target_balance:+,.2f}")
                st.write("---")
            
            # Download transactions
            csv_data = transactions_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Transactions CSV",
                data=csv_data,
                file_name="demo_transactions.csv",
                mime="text/csv"
            )
            
            st.success(f"✅ Generated {len(all_transactions)} balanced transactions!")
        
        # BAI2 Generation button with balance logic
        if bai2_gen and st.button("Generate BAI2 Bank Statement", type="primary", key="generate_bai2_btn"):
            st.info("🏦 Generating BAI2 bank statement with balance logic...")
            
            try:
                # Generate BAI2 content with per-account balances
                bai2_content = bai2_gen.generate_bai2_file(
                    accounts=st.session_state.real_accounts,
                    transactions_per_account=st.session_state.transactions_per_account
                    # opening_balance and target_closing_balance are now handled per-account in the BAI2 generator
                )
                
                # Store BAI2 content in session state
                st.session_state.bai2_content = bai2_content
                
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
        
        # Post to Oracle Fusion button (only show if BAI2 was generated)
        if 'bai2_content' in st.session_state and st.session_state.bai2_content:
            st.markdown("---")
            st.subheader("📤 Post to Oracle Fusion")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Post BAI2 to Oracle Fusion", type="secondary", key="post_bai2_btn"):
                    st.info("📤 Posting BAI2 bank statement to Oracle Fusion...")
                    
                    try:
                        client = SimpleOracleClient(config)
                        
                        # Add authentication if provided in sidebar
                        if 'username' in st.session_state and 'password' in st.session_state:
                            if st.session_state.username and st.session_state.password:
                                client.session.auth = (st.session_state.username, st.session_state.password)
                        
                        # Post to Oracle Fusion
                        success = client.post_bank_statement(st.session_state.bai2_content)
                        
                        if success:
                            st.success("✅ Successfully posted BAI2 to Oracle Fusion!")
                        else:
                            st.error("❌ Failed to post BAI2 to Oracle Fusion")
                            
                    except Exception as e:
                        st.error(f"❌ Error posting to Oracle Fusion: {e}")
            
            with col2:
                if st.button("🔄 Clear BAI2 Data", type="secondary", key="clear_bai2_btn"):
                    if 'bai2_content' in st.session_state:
                        del st.session_state.bai2_content
                    st.rerun()

# Transactions Tab
with tab2:
    st.success("�� **TRANSACTIONS**")
    st.markdown("Generate transactions based on real opening balances")
    
    # Check if we have bank accounts
    if not st.session_state.real_accounts:
        st.warning("⚠️ Please fetch bank accounts from the 'Real Balances' tab first")
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
            
            # Post to Oracle Fusion button (only show if external transactions were generated)
            if st.session_state.external_transactions:
                st.markdown("---")
                st.subheader("📤 Post to Oracle Fusion")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Post External Cash to Oracle Fusion", type="secondary", key="post_external_cash_btn"):
                        st.info("📤 Posting external cash transactions to Oracle Fusion...")
                        
                        try:
                            client = SimpleOracleClient(config)
                            
                            # Add authentication if provided in sidebar
                            if 'username' in st.session_state and 'password' in st.session_state:
                                if st.session_state.username and st.session_state.password:
                                    client.session.auth = (st.session_state.username, st.session_state.password)
                                    st.info("🔐 Using stored credentials")
                            
                            # Post to Oracle Fusion
                            success = client.post_external_cash_transactions(st.session_state.external_transactions)
                            
                            if success:
                                st.success("✅ Successfully posted external cash transactions to Oracle Fusion!")
                            else:
                                st.error("❌ Failed to post external cash transactions to Oracle Fusion")
                                
                        except Exception as e:
                            st.error(f"❌ Error posting to Oracle Fusion: {e}")
                
                with col2:
                    if st.button("🔄 Clear External Cash Data", type="secondary", key="clear_external_cash_btn"):
                        if 'external_transactions' in st.session_state:
                            del st.session_state.external_transactions
                        st.rerun()

# AP Invoices Section
st.subheader("📄 **AP INVOICES**")
st.markdown("Generate AP (Accounts Payable) invoices for Oracle Fusion")

# Check if we have bank accounts
if not st.session_state.real_accounts:
    st.warning("⚠️ Please fetch bank accounts from the 'Real Balances' tab first")
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
            key="ap_invoices_per_account_tab2"
        )
    
    with col2:
        ap_lines_per_invoice = st.number_input(
            "Lines per Invoice",
            min_value=1,
            max_value=10,
            value=st.session_state.ap_lines_per_invoice,
            help="Number of line items per AP invoice",
            key="ap_lines_per_invoice_tab2"
        )
    
    with col3:
        ap_date_range_days = st.number_input(
            "Date Range (Days)",
            min_value=1,
            max_value=90,
            value=30,
            help="Number of days back to generate invoices",
            key="ap_date_range_days_tab2"
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
            
            # Post to Oracle Fusion button (only show if AP invoices were generated)
            if st.session_state.ap_invoices:
                st.markdown("---")
                st.subheader("📤 Post to Oracle Fusion")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Post AP Invoices to Oracle Fusion", type="secondary", key="post_ap_btn"):
                        st.info("📤 Posting AP invoices to Oracle Fusion...")
                        
                        try:
                            client = SimpleOracleClient(config)
                            
                            # Add authentication if provided in sidebar
                            if 'username' in st.session_state and 'password' in st.session_state:
                                if st.session_state.username and st.session_state.password:
                                    client.session.auth = (st.session_state.username, st.session_state.password)
                                    st.info("🔐 Using stored credentials")
                            
                            # Post to Oracle Fusion
                            success = client.post_ap_invoices(st.session_state.ap_invoices)
                            
                            if success:
                                st.success("✅ Successfully posted AP invoices to Oracle Fusion!")
                            else:
                                st.error("❌ Failed to post AP invoices to Oracle Fusion")
                                
                        except Exception as e:
                            st.error(f"❌ Error posting to Oracle Fusion: {e}")
                
                with col2:
                    if st.button("🔄 Clear AP Data", type="secondary", key="clear_ap_btn"):
                        if 'ap_invoices' in st.session_state:
                            del st.session_state.ap_invoices
                        st.rerun()

# AR Invoices/Receipts Section
st.subheader("📋 **AR INVOICES/RECEIPTS**")
st.markdown("Generate AR (Accounts Receivable) invoices and receipts for Oracle Fusion")

# Check if we have bank accounts
if not st.session_state.real_accounts:
    st.warning("⚠️ Please fetch bank accounts from the 'Real Balances' tab first")
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
            key="ar_invoices_per_account_tab2"
        )
    
    with col2:
        ar_lines_per_invoice = st.number_input(
            "Lines per Invoice",
            min_value=1,
            max_value=10,
            value=st.session_state.ar_lines_per_invoice,
            help="Number of line items per AR invoice",
            key="ar_lines_per_invoice_tab2"
        )
    
    with col3:
        ar_date_range_days = st.number_input(
            "Date Range (Days)",
            min_value=1,
            max_value=90,
            value=30,
            help="Number of days back to generate invoices",
            key="ar_date_range_days_tab2"
        )
    
    with col4:
        receipt_percentage = st.slider(
            "Receipt Percentage",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Percentage of invoices that will have receipts",
            key="receipt_percentage_tab2"
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
            
            # Post to Oracle Fusion button (only show if AR invoices were generated)
            if st.session_state.ar_invoices:
                st.markdown("---")
                st.subheader("📤 Post to Oracle Fusion")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Post AR Invoices to Oracle Fusion", type="secondary", key="post_ar_btn"):
                        st.info("📤 Posting AR invoices to Oracle Fusion...")
                        
                        try:
                            client = SimpleOracleClient(config)
                            
                            # Add authentication if provided in sidebar
                            if 'username' in st.session_state and 'password' in st.session_state:
                                if st.session_state.username and st.session_state.password:
                                    client.session.auth = (st.session_state.username, st.session_state.password)
                                    st.info("🔐 Using stored credentials")
                            
                            # Post to Oracle Fusion
                            success = client.post_ar_invoices(st.session_state.ar_invoices)
                            
                            if success:
                                st.success("✅ Successfully posted AR invoices to Oracle Fusion!")
                            else:
                                st.error("❌ Failed to post AR invoices to Oracle Fusion")
                                
                        except Exception as e:
                            st.error(f"❌ Error posting to Oracle Fusion: {e}")
                
                with col2:
                    if st.button("🔄 Clear AR Data", type="secondary", key="clear_ar_btn"):
                        if 'ar_invoices' in st.session_state:
                            del st.session_state.ar_invoices
                        if 'ar_receipts' in st.session_state:
                            del st.session_state.ar_receipts
                        st.rerun()

# GL Journals Section
st.subheader("📊 **GL JOURNALS**")
st.markdown("Generate GL (General Ledger) journal entries for Oracle Fusion")

# Check if we have bank accounts
if not st.session_state.real_accounts:
    st.warning("⚠️ Please fetch bank accounts from the 'Real Balances' tab first")
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
            key="gl_journals_per_account_tab2"
        )
    
    with col2:
        gl_lines_per_journal = st.number_input(
            "Lines per Journal",
            min_value=2,
            max_value=10,
            value=st.session_state.gl_lines_per_journal,
            help="Number of line items per GL journal (minimum 2 for balance)",
            key="gl_lines_per_journal_tab2"
        )
    
    with col3:
        gl_date_range_days = st.number_input(
            "Date Range (Days)",
            min_value=1,
            max_value=90,
            value=30,
            help="Number of days back to generate journals",
            key="gl_date_range_days_tab2"
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
            
            # Post to Oracle Fusion button (only show if GL journals were generated)
            if st.session_state.gl_journals:
                st.markdown("---")
                st.subheader("📤 Post to Oracle Fusion")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Post GL Journals to Oracle Fusion", type="secondary", key="post_gl_btn"):
                        st.info("📤 Posting GL journals to Oracle Fusion...")
                        
                        try:
                            client = SimpleOracleClient(config)
                            
                            # Add authentication if provided in sidebar
                            if 'username' in st.session_state and 'password' in st.session_state:
                                if st.session_state.username and st.session_state.password:
                                    client.session.auth = (st.session_state.username, st.session_state.password)
                                    st.info("🔐 Using stored credentials")
                            
                            # Post to Oracle Fusion
                            success = client.post_gl_journals(st.session_state.gl_journals)
                            
                            if success:
                                st.success("✅ Successfully posted GL journals to Oracle Fusion!")
                            else:
                                st.error("❌ Failed to post GL journals to Oracle Fusion")
                                
                        except Exception as e:
                            st.error(f"❌ Error posting to Oracle Fusion: {e}")
                
                with col2:
                    if st.button("🔄 Clear GL Data", type="secondary", key="clear_gl_btn"):
                        if 'gl_journals' in st.session_state:
                            del st.session_state.gl_journals
                        st.rerun()
