# Oracle Fusion Demo Transaction Generator

A comprehensive Streamlit web application for generating demo transactions for Oracle Fusion Financials testing and development. This tool combines real Oracle Fusion bank account data with realistic fake transactions to create comprehensive test datasets.

## 🚀 Features

### Core Components
- **🏦 Real Bank Accounts**: Fetch and display real bank accounts from Oracle Fusion instance
- **📊 BAI2 Bank Statements**: Generate BAI2 format bank statements with opening/closing balances
- **💳 External Cash Transactions**: Generate cash management transactions for auto-reconciliation
- **📄 AP Invoices**: Create Accounts Payable invoices with line items and supplier data
- **📋 AR Invoices/Receipts**: Generate Accounts Receivable invoices and associated receipts
- **📊 GL Journals**: Create balanced General Ledger journal entries

### Key Features
- **🌐 Streamlit Web Interface**: User-friendly web application with tabbed interface
- **🔗 Oracle Fusion API Integration**: Direct connection to Oracle Fusion instances
- **📊 Multiple Export Formats**: CSV, JSON, and Properties files for Oracle Fusion import
- **⚙️ Configurable Parameters**: Customize transaction counts, amounts, and date ranges
- **🎭 Realistic Data**: Uses Faker library for realistic demo data
- **🔐 Secure Authentication**: Username/password authentication for Oracle Fusion
- **📱 Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
data tests generation/
├── .github/                      # GitHub templates and workflows
├── .streamlit/                   # Streamlit configuration
├── config/
│   └── config.yaml              # Configuration file
├── demo_venv/                   # Virtual environment (ignored by Git)
├── main_fixed.py                # Main Streamlit application
├── bai2_generator.py            # BAI2 bank statement generator
├── external_cash_generator.py   # External cash transactions generator
├── ap_invoice_generator.py      # AP invoice generator
├── ar_invoice_generator.py      # AR invoice generator
├── gl_journal_generator.py      # GL journal generator
├── validate_step2.py            # Step 2 validation script
├── validate_step4.py            # Step 4 validation script
├── validate_step5.py            # Step 5 validation script
├── requirements.txt             # Python dependencies
├── run.bat                     # Windows batch file to run the app
├── .gitignore                  # Git ignore rules
├── LICENSE                     # License file
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Oracle Fusion instance access
- API credentials (username/password)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/mambamota/oracle-fusion-demo-transaction-generator.git
   cd oracle-fusion-demo-transaction-generator
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   - Edit `config/config.yaml` with your Oracle Fusion instance details
   - Update the base URL and API version as needed

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

#### 1. 🏦 Real Bank Accounts Tab
- Enter your Oracle Fusion base URL
- Provide username and password
- Click "Fetch Bank Accounts" to retrieve real account data
- View account details and download raw JSON data
- Use this data as the foundation for generating transactions

#### 2. 📊 BAI2 Bank Statements Tab
- Configure opening and closing balances
- Set the number of transactions to generate
- Generate BAI2 format bank statements
- Download the generated BAI2 file
- Export to Excel for review

#### 3. 💳 External Cash Transactions Tab
- Set the number of transactions per account
- Configure transaction amounts and date ranges
- Generate external cash management transactions
- Download CSV and JSON formats
- Export to Excel for review

#### 4. 📄 AP Invoices Tab
- Set the number of invoices to generate
- Configure line items per invoice
- Generate Accounts Payable invoices with suppliers
- Download CSV, JSON, and Properties files
- Export to Excel for review

#### 5. 📋 AR Invoices/Receipts Tab
- Set the number of invoices and receipts
- Configure line items and customer data
- Generate Accounts Receivable invoices and receipts
- Download CSV, JSON, and Properties files
- Export to Excel for review

#### 6. 📊 GL Journals Tab
- Set the number of journal entries per account
- Configure lines per journal (minimum 2 for balance)
- Generate balanced General Ledger journal entries
- Download CSV, JSON, and Properties files
- Export to Excel for review

## ⚙️ Configuration

### config/config.yaml

```yaml
oracle_fusion:
  base_url: "https://your-instance.fa.ocs.oraclecloud.com"
  api_version: "11.13.18.05"
  timeout: 30

transactions:
  bai2_statement:
    default_transactions: 50
    min_amount: 100.00
    max_amount: 10000.00
    date_range_days: 30
  
  external_cash:
    default_transactions_per_account: 10
    min_amount: 500.00
    max_amount: 5000.00
  
  ap_invoices:
    default_invoices: 20
    default_lines_per_invoice: 3
    min_amount: 500.00
    max_amount: 5000.00
  
  ar_invoices:
    default_invoices: 15
    default_lines_per_invoice: 2
    min_amount: 1000.00
    max_amount: 15000.00
  
  gl_journals:
    default_journals_per_account: 2
    default_lines_per_journal: 3
    min_amount: 100.00
    max_amount: 5000.00
```

## 📊 Generated Data Types

### 🏦 Real Bank Accounts
- Fetched from Oracle Fusion instance
- Account names, numbers, and currencies
- Business unit and ledger information
- Real account data for authentic testing

### 📊 BAI2 Bank Statements
- Multiple bank accounts with real data
- Opening and closing balances
- Random transactions (credits/debits)
- Proper BAI2 record formatting
- Transaction references and descriptions

### 💳 External Cash Transactions
- Cash management transactions
- Transaction types (receipt/payment/transfer)
- Bank account references
- Auto-reconciliation ready
- CSV and JSON export formats

### 📄 AP Invoices
- Supplier information and addresses
- Invoice dates and due dates
- Line items with quantities and prices
- Payment terms and account assignments
- Multiple export formats (CSV, JSON, Properties)

### 📋 AR Invoices/Receipts
- Customer information and addresses
- Invoice details and line items
- Service descriptions and amounts
- Payment terms and account assignments
- Associated receipt generation

### 📊 GL Journals
- Balanced journal entries (debits = credits)
- Multiple account types (Asset, Liability, Equity, Revenue, Expense)
- Journal descriptions and line details
- Business unit and ledger assignments
- Multiple export formats

## 🔧 API Integration

The application integrates with Oracle Fusion REST APIs:

- **Bank Account Fetching**: `fscmRestApi/resources/11.13.18.05/cashBankAccounts`
- **BAI2 Bank Statement Processing**: Upload and process via ESS jobs
- **External Cash Transactions**: Create cash management transactions
- **AP Invoices**: Create Accounts Payable invoices
- **AR Invoices**: Create Accounts Receivable invoices
- **GL Journals**: Create General Ledger journal entries

## 📤 Posting Features

### Direct Posting to Oracle Fusion

The application now supports **direct posting** of generated data back to your Oracle Fusion instance:

#### Prerequisites for Posting
- Valid Oracle Fusion instance URL
- Username and password with posting permissions
- Generated data in any of the tabs

#### Posting Process
1. **Generate Data**: Use any tab to generate demo data
2. **Review Data**: Check the generated data in the interface
3. **Post to Fusion**: Click the "Post to Oracle Fusion" button
4. **Monitor Status**: Watch for success/error messages
5. **Verify in Fusion**: Check your Oracle Fusion instance for posted data

#### Supported Posting Operations
- **🏦 BAI2 Bank Statements**: Post bank statement data
- **💳 External Cash**: Post cash management transactions
- **📄 AP Invoices**: Post accounts payable invoices
- **📋 AR Invoices**: Post accounts receivable invoices
- **📊 GL Journals**: Post general ledger journal entries

#### Endpoint Discovery
The app includes an **"Discover Available Endpoints"** button in the sidebar that:
- Tests common Oracle Fusion REST API endpoints
- Identifies which endpoints are available in your instance
- Shows authentication requirements for each endpoint
- Helps determine which posting features are available

#### Error Handling
- **Authentication Errors**: Check username/password
- **Permission Errors**: Verify posting permissions
- **Data Format Errors**: Review generated data structure
- **Network Errors**: Check Oracle Fusion connectivity
- **404 Errors**: Endpoint not available in your instance

#### Data Flow
1. **📥 Fetch Real Data**: Get real bank accounts from Oracle Fusion
2. **🎭 Generate Fake Data**: Create realistic transaction data
3. **🔗 Combine Data**: Merge real accounts with fake transactions
4. **📤 Post Back**: Send combined data to Oracle Fusion for testing

## 📁 Output Files

Generated files include:
- `bank_statement.bai2`: BAI2 format bank statement
- `external_cash_transactions.csv`: External cash transactions
- `ap_invoices_interface.csv`: AP invoice data
- `ap_invoice_import.properties`: AP import configuration
- `ar_invoices_interface.csv`: AR invoice data
- `ar_invoice_import.properties`: AR import configuration
- `gl_journals_interface.csv`: GL journal data
- `gl_journal_import.properties`: GL import configuration
- Various Excel files for review and analysis

## 🛡️ Security Notes

- **Credentials**: Enter username/password in the web interface (not stored permanently)
- **Base URL**: Configurable Oracle Fusion instance URL
- **Data Privacy**: Sample data files are kept locally and not pushed to GitHub
- **Testing**: Always test in development environment first
- **Review**: Review generated data before production use

## 🧪 Validation Scripts

The project includes validation scripts for each component:
- `validate_step2.py`: External Cash Transactions validation
- `validate_step4.py`: AR Invoices validation
- `validate_step5.py`: GL Journals validation

Run these scripts to verify data generation:
```bash
python validate_step2.py
python validate_step4.py
python validate_step5.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly using validation scripts
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues or questions:
1. Check the configuration file (`config/config.yaml`)
2. Verify Oracle Fusion connection and credentials
3. Review error logs in the Streamlit interface
4. Test with smaller data sets first
5. Run validation scripts to verify functionality

## 🔄 Version History

- **V1.0**: Initial release with bank statement generation
- **V1.1**: Added external cash transactions
- **V1.2**: Added AP invoice generation
- **V1.3**: Added AR invoice and receipt generation
- **V2.0**: Added GL journal generation and comprehensive validation
- **V2.1**: Enhanced UI, improved error handling, and added multiple export formats

## 🚀 Deployment

### Local Development
```bash
streamlit run main_fixed.py
```

### Streamlit Cloud Deployment
1. Push to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy automatically from GitHub

### Environment Variables
- No environment variables required
- All configuration through web interface
- Credentials entered securely in the app

---

**Note**: This tool is designed for Oracle Fusion Financials testing and development. Always review generated data before using in production environments. 