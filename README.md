# Oracle Fusion Demo Transaction Generator

A comprehensive tool for generating demo transactions for Oracle Fusion Financials testing and development.

## 🚀 Features

### Core Components
- **Bank Statement Generator (V1)**: Creates BAI2 format bank statements with opening/closing balances
- **External Cash Transactions (V1)**: Generates cash management transactions for auto-reconciliation
- **AP Invoices (V1.1)**: Creates Accounts Payable invoices with line items
- **AR Invoices/Receipts (V1.2)**: Generates Accounts Receivable invoices and receipts
- **GL Journals (V2)**: Creates General Ledger journal entries

### Key Features
- **Streamlit Web Interface**: User-friendly web application
- **Excel Export**: Export generated data to Excel files for review
- **Oracle Fusion API Integration**: Direct connection to Oracle Fusion instances
- **Configurable Parameters**: Customize transaction counts, amounts, and date ranges
- **Realistic Data**: Uses Faker library for realistic demo data
- **BAI2 Format Support**: Proper BAI2 bank statement format generation

## 📁 Project Structure

```
data tests generation/
├── config/
│   └── config.yaml              # Configuration file
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── oracle_client.py     # Oracle Fusion API client
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── bai2_generator.py   # BAI2 bank statement generator
│   │   └── transaction_generators.py  # Transaction generators
│   ├── utils/
│   │   ├── __init__.py
│   │   └── excel_exporter.py    # Excel export utilities
│   └── __init__.py
├── main.py                      # Main Streamlit application
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Oracle Fusion instance access
- API credentials

### Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd "data tests generation"
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
   - Update the base URL and other settings as needed

## 🚀 Usage

### Starting the Application

1. **Run the Streamlit app**
   ```bash
   streamlit run main.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:8501`
   - The application will open automatically

### Using the Application

#### 1. Oracle Fusion Connection
- Enter your Oracle Fusion instance URL
- Provide username and password
- Test the connection using the "Test Connection" button

#### 2. Bank Statement Generation
- Navigate to the "Bank Statements" tab
- Configure:
  - Number of bank accounts
  - Transactions per account
  - Minimum/maximum transaction amounts
- Generate BAI2 format bank statements
- Download the generated file

#### 3. AP Invoice Generation
- Navigate to the "AP Invoices" tab
- Set the number of invoices to generate
- Generate Accounts Payable invoices
- Export to Excel for review

#### 4. AR Invoice Generation
- Navigate to the "AR Invoices" tab
- Set the number of invoices to generate
- Generate Accounts Receivable invoices
- Export to Excel for review

#### 5. GL Journal Generation
- Navigate to the "GL Journals" tab
- Set the number of journal entries to generate
- Generate General Ledger journal entries
- Export to Excel for review

#### 6. Export All Data
- Navigate to the "Export Data" tab
- Generate all transaction types at once
- Download comprehensive Excel file with all data

## ⚙️ Configuration

### config/config.yaml

```yaml
oracle_fusion:
  base_url: "https://your-instance.oraclecloud.com"
  api_version: "v1"
  timeout: 30

transactions:
  bank_statement:
    default_count: 50
    min_amount: 100.00
    max_amount: 10000.00
    date_range_days: 30
  
  ap_invoices:
    default_count: 20
    min_amount: 500.00
    max_amount: 5000.00
  
  ar_invoices:
    default_count: 15
    min_amount: 1000.00
    max_amount: 15000.00
  
  gl_journals:
    default_count: 10
    min_amount: 100.00
    max_amount: 5000.00
```

## 📊 Generated Data Types

### Bank Statements (BAI2 Format)
- Multiple bank accounts
- Opening and closing balances
- Random transactions (credits/debits)
- Proper BAI2 record formatting
- Transaction references and descriptions

### AP Invoices
- Supplier information
- Invoice dates and due dates
- Line items with quantities and prices
- Payment terms
- Account assignments

### AR Invoices
- Customer information
- Invoice details
- Service line items
- Payment terms
- Account assignments

### GL Journals
- Journal entries with proper debits/credits
- Account combinations
- Balanced entries
- Journal descriptions

### External Cash Transactions
- Cash management transactions
- Transaction types (receipt/payment/transfer)
- Bank account references
- Auto-reconciliation ready

## 🔧 API Integration

The application integrates with Oracle Fusion APIs:

- **Bank Statement Processing**: Upload BAI2 files and process via ESS jobs
- **External Cash Transactions**: Create cash management transactions
- **AP Invoices**: Create Accounts Payable invoices
- **AR Invoices**: Create Accounts Receivable invoices
- **GL Journals**: Create General Ledger journal entries

## 📁 Output Files

Generated files include:
- `generated_bank_statement.bai2`: BAI2 format bank statement
- `ap_invoices_YYYYMMDD_HHMMSS.xlsx`: AP invoices Excel file
- `ar_invoices_YYYYMMDD_HHMMSS.xlsx`: AR invoices Excel file
- `gl_journals_YYYYMMDD_HHMMSS.xlsx`: GL journals Excel file
- `demo_transactions_YYYYMMDD_HHMMSS.xlsx`: Complete transaction data

## 🛡️ Security Notes

- Store credentials securely
- Use environment variables for sensitive data
- Test in development environment first
- Review generated data before production use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for internal use and testing purposes.

## 🆘 Support

For issues or questions:
1. Check the configuration file
2. Verify Oracle Fusion connection
3. Review error logs
4. Test with smaller data sets first

## 🔄 Version History

- **V1**: Bank statement generation and external cash transactions
- **V1.1**: AP invoice generation
- **V1.2**: AR invoice and receipt generation
- **V2**: GL journal generation and comprehensive Excel export 