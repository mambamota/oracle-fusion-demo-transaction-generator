# Oracle Fusion Demo Transaction Generator

A comprehensive Streamlit web application for generating demo transactions for Oracle Fusion Financials testing and development. This tool fetches **real opening balances** from Oracle Fusion and generates realistic fake transactions to create comprehensive test datasets.

## 🚀 Features

### Core Components
- **💰 Real Opening Balances**: Fetch real opening balances per bank account per day from Oracle Fusion using BIP Publisher
- **🏦 Real Bank Accounts**: Fetch and display real bank accounts from Oracle Fusion instance
- **📊 BAI2 Bank Statements**: Generate BAI2 format bank statements with real opening balances
- **💳 External Cash Transactions**: Generate cash management transactions for auto-reconciliation
- **📄 AP Invoices**: Create Accounts Payable invoices with line items and supplier data
- **📋 AR Invoices/Receipts**: Generate Accounts Receivable invoices and associated receipts
- **📊 GL Journals**: Create balanced General Ledger journal entries

### Key Features
- **🌐 Streamlit Web Interface**: User-friendly web application with simplified tabbed interface
- **🔗 Oracle Fusion API Integration**: Direct connection to Oracle Fusion instances
- **📊 BIP Publisher Integration**: Fetch real opening balances via Oracle Business Intelligence Publisher
- **📊 Multiple Export Formats**: CSV, JSON, and Properties files for Oracle Fusion import
- **⚙️ Configurable Parameters**: Customize transaction counts, amounts, and date ranges
- **🎭 Realistic Data**: Uses Faker library for realistic demo data
- **🔐 Secure Authentication**: Username/password authentication for Oracle Fusion
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🚀 Streamlit Share Ready**: Deployable on Streamlit Cloud with secrets management

## 📁 Project Structure

```
data tests generation/
├── .github/                      # GitHub templates and workflows
├── .streamlit/                   # Streamlit configuration
│   └── config.toml              # Streamlit deployment config
├── config/
│   └── config.yaml              # Configuration file
├── search_files/                 # Development and discovery files
├── main_fixed.py                # Main Streamlit application
├── bai2_generator.py            # BAI2 bank statement generator
├── bip_balance_client.py        # BIP Publisher client
├── test_bip_working_path.py     # BIP Publisher test script
├── test_working_opening_balances.py # REST API test script
├── final_opening_balance_query.sql # SQL query for opening balances
├── requirements.txt             # Python dependencies
├── bip_config.env              # BIP Publisher credentials (local only)
├── .gitignore                  # Git ignore rules
├── LICENSE                     # License file
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Oracle Fusion instance access
- API credentials (username/password)
- BIP Publisher access (for real balance fetching)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/mbola-raoelina/oracle-fusion-demo-transaction-generator.git
   cd oracle-fusion-demo-transaction-generator
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv demo_venv
   
   # On Windows
   demo_venv\Scripts\activate
   
   # On macOS/Linux
   source demo_venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   - Edit `config/config.yaml` with your Oracle Fusion instance details
   - Create `bip_config.env` with your BIP Publisher credentials (see Configuration section)

## 🚀 Usage

### Starting the Application

1. **Run the Streamlit app**
   ```bash
   streamlit run main_fixed.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`
   - The application will open automatically

### Using the Application

#### 1. 💰 Real Balances Tab
- **Test Oracle Connection**: Verify connectivity to your Oracle Fusion instance
- **Test BIP Publisher**: Verify BIP Publisher access for real balance fetching
- **Fetch Real Bank Accounts**: Get real bank accounts with opening balances
- **Set Target Closing Balances**: Configure target balances for each account
- **Generate Demo Transactions**: Create transactions that balance from real opening to target closing

#### 2. 💳 Transactions Tab
- **External Cash Transactions**: Generate cash management transactions
- **AP Invoices**: Create Accounts Payable invoices with suppliers
- **AR Invoices/Receipts**: Generate Accounts Receivable invoices and receipts
- **GL Journals**: Create balanced General Ledger journal entries
- **Post to Oracle Fusion**: Send generated data directly to your Oracle Fusion instance

## ⚙️ Configuration

### Local Development (bip_config.env)
```env
BIP_BASE_URL=https://your-instance.fa.ocs.oraclecloud.com
BIP_ENDPOINT=https://your-instance.fa.ocs.oraclecloud.com:443/xmlpserver/services/v2/ReportService
BIP_REPORT_PATH=/~your-username/_temp/wsq/csv.xdo
BIP_USERNAME=your-username@your-domain.com
BIP_PASSWORD=your-password
```

### Streamlit Share Deployment (Secrets)
```toml
[oracle_fusion]
username = "your-oracle-username"
password = "your-oracle-password"
base_url = "https://your-instance.fa.ocs.oraclecloud.com"

[bip_publisher]
username = "your-bip-username"
password = "your-bip-password"
base_url = "https://your-instance.fa.ocs.oraclecloud.com"
endpoint = "https://your-instance.fa.ocs.oraclecloud.com:443/xmlpserver/services/v2/ReportService"
report_path = "/~your-username/_temp/wsq/csv.xdo"
```

### config/config.yaml
```yaml
oracle_fusion:
  base_url: "https://your-instance.fa.ocs.oraclecloud.com"
  api_version: "11.13.18.05"
  timeout: 30

transactions:
  default_per_account: 10
  default_opening_balance: 50000.0
  default_closing_balance: 75000.0
```

## 🔧 Technical Architecture

### Real Balance Fetching
The application uses **Oracle BIP Publisher** to fetch real opening balances:

1. **SQL Query**: Queries `CE_STMT_BALANCES` table for opening balances (`OPBD`)
2. **BIP Publisher**: Sends SQL via SOAP request to BIP Publisher service
3. **Data Processing**: Parses CSV response and matches to bank accounts
4. **Fallback**: Uses REST API if BIP Publisher is unavailable

### Balance Matching Logic
- **REST API**: Fetches bank accounts via `cashBankAccounts` endpoint
- **BIP Data**: Fetches opening balances via BIP Publisher
- **Matching**: Links accounts using `bank_account_id` with multiple strategies
- **Fallback**: Uses default balance if no match found

### Transaction Generation
- **Real Opening Balances**: Uses actual balances from Oracle Fusion
- **Target Closing Balances**: User-defined targets for each account
- **Mathematical Balance**: Generates transactions that balance from opening to target
- **Realistic Data**: Uses Faker library for realistic transaction details

## 📊 Generated Data Types

### 💰 Real Opening Balances
- **Source**: Oracle Fusion `CE_STMT_BALANCES` table
- **Method**: BIP Publisher SQL query
- **Format**: Latest opening balance per bank account per day
- **Features**: Supports negative balances, multiple currencies

### 🏦 Real Bank Accounts
- **Source**: Oracle Fusion REST API
- **Endpoint**: `cashBankAccounts`
- **Data**: Account names, numbers, currencies, business units
- **Integration**: Matched with BIP opening balances

### 📊 BAI2 Bank Statements
- **Real Opening Balances**: Uses actual balances from Fusion
- **Target Closing Balances**: User-configurable targets
- **Transaction Generation**: Creates balanced transactions
- **Format**: Standard BAI2 format for bank statement import

### 💳 External Cash Transactions
- **Cash Management**: Transactions for auto-reconciliation
- **Transaction Types**: Receipt, payment, transfer
- **Bank Account References**: Links to real bank accounts
- **Export Formats**: CSV, JSON for Oracle Fusion import

### 📄 AP Invoices
- **Supplier Information**: Realistic supplier data
- **Line Items**: Quantities, prices, descriptions
- **Payment Terms**: Configurable payment terms
- **Export Formats**: CSV, JSON, Properties files

### 📋 AR Invoices/Receipts
- **Customer Information**: Realistic customer data
- **Invoice Details**: Line items, amounts, descriptions
- **Receipt Generation**: Associated receipt creation
- **Export Formats**: CSV, JSON, Properties files

### 📊 GL Journals
- **Balanced Entries**: Debits equal credits
- **Account Types**: Asset, Liability, Equity, Revenue, Expense
- **Business Units**: Configurable business unit assignments
- **Export Formats**: CSV, JSON, Properties files

## 🚀 Deployment

### Local Development
```bash
streamlit run main_fixed.py
```

### Streamlit Share Deployment

1. **Upload Files to Streamlit Share:**
   ```
   main_fixed.py
   config/config.yaml
   bai2_generator.py
   requirements.txt
   .streamlit/config.toml
   final_opening_balance_query.sql
   test_bip_working_path.py
   test_working_opening_balances.py
   bip_balance_client.py
   README.md
   ```

2. **Configure Secrets in Streamlit Share:**
   - Go to your app → Settings → Secrets
   - Add the secrets configuration shown above
   - Replace with your actual Oracle Fusion credentials

3. **Deploy:**
   - Click "Deploy"
   - Your app will be available at: `https://your-app-name.streamlit.app`

## 🔧 API Integration

The application integrates with Oracle Fusion using multiple methods:

### REST APIs
- **Bank Account Fetching**: `fscmRestApi/resources/11.13.18.05/cashBankAccounts`
- **Posting Operations**: Direct posting to Oracle Fusion endpoints

### BIP Publisher
- **Opening Balances**: SQL queries via BIP Publisher service
- **Endpoint**: `xmlpserver/services/v2/ReportService`
- **Method**: SOAP requests with GZIP/Base64 encoded SQL

### Database Tables
- **`CE_STMT_BALANCES`**: Opening balances with `OPBD` code
- **`GL_BALANCES`**: General ledger balances
- **`all_tables`**: Schema discovery

## 📤 Posting Features

### Direct Posting to Oracle Fusion

The application supports **direct posting** of generated data back to your Oracle Fusion instance:

#### Supported Posting Operations
- **🏦 BAI2 Bank Statements**: Post bank statement data
- **💳 External Cash**: Post cash management transactions
- **📄 AP Invoices**: Post accounts payable invoices
- **📋 AR Invoices**: Post accounts receivable invoices
- **📊 GL Journals**: Post general ledger journal entries

#### Posting Process
1. **Generate Data**: Use any tab to generate demo data
2. **Review Data**: Check the generated data in the interface
3. **Post to Fusion**: Click the "Post to Oracle Fusion" button
4. **Monitor Status**: Watch for success/error messages
5. **Verify in Fusion**: Check your Oracle Fusion instance for posted data

## 🛡️ Security Notes

- **Credentials**: Stored in Streamlit secrets for deployment, environment variables for local development
- **Base URL**: Configurable Oracle Fusion instance URL
- **Data Privacy**: Sample data files are kept locally and not pushed to GitHub
- **Testing**: Always test in development environment first
- **Review**: Review generated data before production use

## 🧪 Testing

### Test Scripts
- `test_bip_working_path.py`: Test BIP Publisher connection
- `test_working_opening_balances.py`: Test REST API balance fetching

### Validation
- **Connection Testing**: Verify Oracle Fusion connectivity
- **Balance Fetching**: Test real opening balance retrieval
- **Transaction Generation**: Validate mathematical balance
- **Data Export**: Verify export format correctness

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly using test scripts
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues or questions:
1. Check the configuration files (`config/config.yaml`, `bip_config.env`)
2. Verify Oracle Fusion connection and credentials
3. Test BIP Publisher access
4. Review error logs in the Streamlit interface
5. Run test scripts to verify functionality

## 🔄 Version History

- **V1.0**: Initial release with bank statement generation
- **V1.1**: Added external cash transactions
- **V1.2**: Added AP invoice generation
- **V1.3**: Added AR invoice and receipt generation
- **V2.0**: Added GL journal generation and comprehensive validation
- **V2.1**: Enhanced UI, improved error handling, and added multiple export formats
- **V3.0**: **Real opening balance fetching via BIP Publisher**
- **V3.1**: **Streamlit Share deployment support with secrets management**

## 🎯 Key Improvements in V3.0

### Real Data Integration
- ✅ **Real Opening Balances**: Fetched from Oracle Fusion via BIP Publisher
- ✅ **Real Bank Accounts**: Retrieved from Oracle Fusion REST APIs
- ✅ **Mathematical Balance**: Transactions balance from real opening to target closing
- ✅ **Negative Balance Support**: Handles negative opening balances properly

### Enhanced User Experience
- ✅ **Simplified Interface**: Clean, minimal UI with essential information only
- ✅ **Real-time Balance Display**: Shows actual balances from Oracle Fusion
- ✅ **Target Balance Configuration**: User-defined closing balance targets
- ✅ **Transaction Verification**: Mathematical balance verification

### Deployment Ready
- ✅ **Streamlit Share Compatible**: Secrets management for secure deployment
- ✅ **Environment Variable Support**: Local development with .env files
- ✅ **Security Hardened**: No hardcoded credentials in code
- ✅ **Production Ready**: Comprehensive error handling and validation

---

**Note**: This tool is designed for Oracle Fusion Financials testing and development. Always review generated data before using in production environments. The application now uses **real opening balances** from your Oracle Fusion instance for authentic testing scenarios. 