#!/usr/bin/env python3
"""
BIP Balance Client for Oracle Fusion
Adapted from bip_vscode project for fetching opening balances
"""

import requests
import gzip
import base64
import xml.etree.ElementTree as ET
import pandas as pd
from io import BytesIO
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('bip_config.env')

class BIPBalanceClient:
    def __init__(self):
        self.base_url = os.getenv('BIP_BASE_URL', 'https://your-instance.fa.ocs.oraclecloud.com')
        self.endpoint = os.getenv('BIP_ENDPOINT', f"{self.base_url}:443/xmlpserver/services/v2/ReportService")
        self.report_path = os.getenv('BIP_REPORT_PATH', '/~your-username/_temp/wsq/csv.xdo')
        self.username = os.getenv('BIP_USERNAME', 'your-username@your-domain.com')
        self.password = os.getenv('BIP_PASSWORD', 'your-password')
        
    def minify_sql(self, sql_query):
        """Minify SQL query by removing comments and extra whitespace"""
        # Remove single-line comments
        sql = re.sub(r'--[^\n]*', '', sql_query)
        # Remove multi-line comments
        sql = re.sub(r'/\*[\s\S]*?\*/', '', sql)
        # Remove extra whitespace
        sql = re.sub(r'\s+', ' ', sql)
        return sql.strip()
    
    def encode_sql(self, sql_query):
        """Compress and encode SQL query for BIP"""
        minified_sql = self.minify_sql(sql_query)
        
        # Compress with gzip
        buf = BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb', mtime=0) as f:
            f.write(minified_sql.encode('utf-8'))
        
        # Encode to base64
        encoded_sql = base64.b64encode(buf.getvalue()).decode('utf-8')
        return encoded_sql
    
    def create_soap_request(self, encoded_sql):
        """Create SOAP request for BIP Publisher"""
        soap_request = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v2="http://xmlns.oracle.com/oxp/service/v2">
   <soapenv:Header/>
   <soapenv:Body>
      <v2:runReport>
         <v2:reportRequest>
            <v2:reportAbsolutePath>{self.report_path}</v2:reportAbsolutePath>
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
         <v2:userID>{self.username}</v2:userID>
         <v2:password>{self.password}</v2:password>
      </v2:runReport>
   </soapenv:Body>
</soapenv:Envelope>'''
        return soap_request
    
    def execute_query(self, sql_query):
        """Execute SQL query via BIP Publisher"""
        print(f"🔍 Executing SQL query via BIP Publisher...")
        print(f"📋 SQL: {sql_query[:100]}...")
        
        try:
            # Encode SQL
            encoded_sql = self.encode_sql(sql_query)
            
            # Create SOAP request
            soap_request = self.create_soap_request(encoded_sql)
            
            # Set headers
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'runReport'
            }
            
            # Send request
            print(f"📤 Sending request to: {self.endpoint}")
            response = requests.post(
                self.endpoint, 
                data=soap_request.encode('utf-8'), 
                headers=headers, 
                timeout=30
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse SOAP response
                root = ET.fromstring(response.text)
                namespaces = {
                    'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                    'v2': 'http://xmlns.oracle.com/oxp/service/v2'
                }
                
                # Extract report data
                report_data = root.find('.//v2:reportBytes', namespaces)
                if report_data is not None and report_data.text:
                    # Decode and parse the report data
                    decoded_data = base64.b64decode(report_data.text)
                    
                    # Try to parse as CSV
                    try:
                        df = pd.read_csv(BytesIO(decoded_data), delimiter='|', encoding='utf-8', dtype=str)
                        df = df.dropna(axis=1, how="all")
                        df = df.fillna('')
                        
                        print(f"✅ Query executed successfully!")
                        print(f"📊 Found {len(df)} records")
                        print("📋 Sample data:")
                        print(df.head().to_string())
                        
                        return df
                    except Exception as csv_error:
                        print(f"⚠️ Could not parse CSV data: {csv_error}")
                        return None
                else:
                    print("⚠️ No report data found in BIP response")
                    print(f"🔍 Response content: {response.text[:500]}...")
                    return None
            else:
                print(f"❌ BIP request failed with status {response.status_code}")
                print(f"🔍 Error response: {response.text[:1000]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return None
    
    def test_connection(self):
        """Test BIP Publisher connection with simple query"""
        print("🧪 Testing BIP Publisher Connection...")
        
        test_sql = "SELECT 1 as test_value FROM dual"
        result = self.execute_query(test_sql)
        
        if result is not None:
            print("✅ BIP Publisher connection successful!")
            return True
        else:
            print("❌ BIP Publisher connection failed!")
            return False
    
    def get_opening_balances(self):
        """Get opening balances using the working SQL query"""
        print("💰 Fetching Opening Balances...")
        
        opening_balance_sql = '''
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
        
        result = self.execute_query(opening_balance_sql)
        
        if result is not None:
            # Save to CSV
            result.to_csv("bip_opening_balances.csv", index=False)
            print("💾 Results saved to: bip_opening_balances.csv")
        
        return result

def main():
    """Main function"""
    print("🏦 Oracle Fusion BIP Balance Client")
    print("=" * 60)
    
    client = BIPBalanceClient()
    
    # Test connection first
    if client.test_connection():
        # Get opening balances
        balances = client.get_opening_balances()
        
        if balances is not None:
            print("\n✅ **SUCCESS!**")
            print("   1. BIP Publisher connection works!")
            print("   2. Opening balances fetched successfully!")
            print("   3. Results saved to CSV file")
        else:
            print("\n❌ Failed to fetch opening balances")
    else:
        print("\n❌ BIP Publisher connection failed")
        print("💡 **Next Steps:**")
        print("   1. Check if report file exists in Oracle Fusion")
        print("   2. Verify credentials and endpoint")
        print("   3. Use simple bank accounts approach instead")

if __name__ == "__main__":
    main() 