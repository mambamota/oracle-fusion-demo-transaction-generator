"""
Oracle Fusion API Client
Handles authentication and API calls to Oracle Fusion Financials
"""

import requests
import json
import yaml
from typing import Dict, Any, Optional
from datetime import datetime
import logging

class OracleFusionClient:
    def __init__(self, base_url: str, username: str, password: str, config_path: str = "config/config.yaml"):
        """
        Initialize Oracle Fusion API client
        
        Args:
            base_url: Oracle Fusion instance URL
            username: API username
            password: API password
            config_path: Path to configuration file
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.token_expiry = None
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self) -> bool:
        """
        Authenticate with Oracle Fusion and get access token
        
        Returns:
            bool: True if authentication successful
        """
        try:
            auth_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/erpintegrations"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Basic authentication
            self.session.auth = (self.username, self.password)
            
            # Test connection
            response = self.session.get(auth_url, headers=headers, timeout=self.config['oracle_fusion']['timeout'])
            
            if response.status_code == 200:
                self.logger.info("Authentication successful")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False
    
    def upload_bank_statement(self, file_path: str) -> Dict[str, Any]:
        """
        Upload bank statement file to UCM server
        
        Args:
            file_path: Path to BAI2 file
            
        Returns:
            Dict containing upload response
        """
        try:
            upload_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/erpintegrations"
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(upload_url, files=files)
                
            if response.status_code == 200:
                self.logger.info("Bank statement uploaded successfully")
                return {'success': True, 'data': response.json()}
            else:
                self.logger.error(f"Upload failed: {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            self.logger.error(f"Upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_bank_statement(self, file_id: str) -> Dict[str, Any]:
        """
        Execute ESS job to process uploaded bank statement
        
        Args:
            file_id: ID of uploaded file
            
        Returns:
            Dict containing processing response
        """
        try:
            process_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/erpintegrations"
            
            payload = {
                "jobName": "BankStatementProcessingForCloud",
                "fileId": file_id
            }
            
            response = self.session.post(process_url, json=payload)
            
            if response.status_code == 200:
                self.logger.info("Bank statement processing initiated")
                return {'success': True, 'data': response.json()}
            else:
                self.logger.error(f"Processing failed: {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_external_cash_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create external cash management transaction
        
        Args:
            transaction_data: Transaction details
            
        Returns:
            Dict containing creation response
        """
        try:
            api_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/externalCashTransactions"
            
            response = self.session.post(api_url, json=transaction_data)
            
            if response.status_code in [200, 201]:
                self.logger.info("External cash transaction created successfully")
                return {'success': True, 'data': response.json()}
            else:
                self.logger.error(f"Creation failed: {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            self.logger.error(f"Creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_ap_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create AP invoice
        
        Args:
            invoice_data: Invoice details
            
        Returns:
            Dict containing creation response
        """
        try:
            api_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/invoices"
            
            response = self.session.post(api_url, json=invoice_data)
            
            if response.status_code in [200, 201]:
                self.logger.info("AP invoice created successfully")
                return {'success': True, 'data': response.json()}
            else:
                self.logger.error(f"Creation failed: {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            self.logger.error(f"Creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_ar_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create AR invoice
        
        Args:
            invoice_data: Invoice details
            
        Returns:
            Dict containing creation response
        """
        try:
            api_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/receivablesInvoices"
            
            response = self.session.post(api_url, json=invoice_data)
            
            if response.status_code in [200, 201]:
                self.logger.info("AR invoice created successfully")
                return {'success': True, 'data': response.json()}
            else:
                self.logger.error(f"Creation failed: {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            self.logger.error(f"Creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_gl_journal(self, journal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create GL journal entry
        
        Args:
            journal_data: Journal details
            
        Returns:
            Dict containing creation response
        """
        try:
            api_url = f"{self.base_url}/fscmRestApi/resources/11.13.18.05/journalEntries"
            
            response = self.session.post(api_url, json=journal_data)
            
            if response.status_code in [200, 201]:
                self.logger.info("GL journal created successfully")
                return {'success': True, 'data': response.json()}
            else:
                self.logger.error(f"Creation failed: {response.status_code} - {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            self.logger.error(f"Creation error: {str(e)}")
            return {'success': False, 'error': str(e)} 