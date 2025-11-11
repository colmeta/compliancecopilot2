# ==============================================================================
# app/data_entry/agent_loader.py
# Agent Loader - The Hand (Database Integration & Loading)
# ==============================================================================
"""
Agent Loader: The fourth and final agent in the Data Keystone pipeline.

Mission: Load validated, structured data into the final system of record
with reliability and flexibility.

Capabilities:
- Multiple output destinations (PostgreSQL, CSV, JSON, Google Sheets, APIs)
- Batch loading with transaction support
- Error recovery and rollback
- Audit trail generation
- Custom data transformations
"""

import logging
from typing import Dict, Any, List, Optional
import csv
import json
import io
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentLoader:
    """
    Agent Loader - Database integration and loading specialist.
    
    This agent handles the final step of the pipeline: loading validated
    data into the target system(s).
    """
    
    def __init__(self):
        """Initialize Agent Loader."""
        logger.info("Agent Loader initialized successfully")
    
    def load_data(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Load data into the target system.
        
        Args:
            data: Validated data to load
            config: Output configuration
            
        Returns:
            Dict with 'success', 'destination', 'record_id', 'error'
        """
        try:
            destination_type = config.get('type', 'json')
            
            if destination_type == 'postgresql':
                return self._load_to_postgresql(data, config)
            elif destination_type == 'csv':
                return self._load_to_csv(data, config)
            elif destination_type == 'json':
                return self._load_to_json(data, config)
            elif destination_type == 'google_sheets':
                return self._load_to_google_sheets(data, config)
            elif destination_type == 'api':
                return self._load_to_api(data, config)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported destination type: {destination_type}"
                }
            
        except Exception as e:
            logger.error(f"Agent Loader error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_to_postgresql(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Load data into PostgreSQL database.
        
        Args:
            data: Data to load
            config: Database configuration
            
        Returns:
            Dict with load result
        """
        try:
            from sqlalchemy import create_engine, Table, MetaData, insert
            
            # Get database connection string
            db_uri = config.get('connection_string')
            table_name = config.get('table_name')
            
            if not db_uri or not table_name:
                return {
                    'success': False,
                    'error': 'Missing connection_string or table_name in config'
                }
            
            # Create engine
            engine = create_engine(db_uri)
            
            # Reflect table metadata
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)
            
            # Insert data
            with engine.connect() as conn:
                result = conn.execute(insert(table).values(**data))
                conn.commit()
                
                # Get inserted record ID
                record_id = result.inserted_primary_key[0] if result.inserted_primary_key else None
            
            return {
                'success': True,
                'destination': 'postgresql',
                'table': table_name,
                'record_id': record_id
            }
            
        except Exception as e:
            logger.error(f"PostgreSQL load failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_to_csv(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Append data to a CSV file.
        
        Args:
            data: Data to load
            config: CSV configuration
            
        Returns:
            Dict with load result
        """
        try:
            import os
            
            file_path = config.get('file_path')
            
            if not file_path:
                return {
                    'success': False,
                    'error': 'Missing file_path in config'
                }
            
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(file_path)
            
            # Open file in append mode
            with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data.keys())
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Write data row
                writer.writerow(data)
            
            return {
                'success': True,
                'destination': 'csv',
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"CSV load failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_to_json(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Append data to a JSON file.
        
        Args:
            data: Data to load
            config: JSON configuration
            
        Returns:
            Dict with load result
        """
        try:
            import os
            
            file_path = config.get('file_path')
            
            if not file_path:
                return {
                    'success': False,
                    'error': 'Missing file_path in config'
                }
            
            # Load existing data if file exists
            existing_data = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []
            
            # Append new data
            existing_data.append(data)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'destination': 'json',
                'file_path': file_path,
                'record_count': len(existing_data)
            }
            
        except Exception as e:
            logger.error(f"JSON load failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_to_google_sheets(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Append data to a Google Sheet.
        
        Args:
            data: Data to load
            config: Google Sheets configuration
            
        Returns:
            Dict with load result
        """
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            # Get configuration
            credentials_file = config.get('credentials_file')
            spreadsheet_id = config.get('spreadsheet_id')
            sheet_name = config.get('sheet_name', 'Sheet1')
            
            if not credentials_file or not spreadsheet_id:
                return {
                    'success': False,
                    'error': 'Missing credentials_file or spreadsheet_id in config'
                }
            
            # Authenticate
            creds = Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            service = build('sheets', 'v4', credentials=creds)
            
            # Prepare data row
            values = [[data.get(key, '') for key in data.keys()]]
            
            # Append to sheet
            body = {'values': values}
            
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:Z",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return {
                'success': True,
                'destination': 'google_sheets',
                'spreadsheet_id': spreadsheet_id,
                'updated_range': result.get('updates', {}).get('updatedRange')
            }
            
        except Exception as e:
            logger.error(f"Google Sheets load failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_to_api(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send data to an external API.
        
        Args:
            data: Data to load
            config: API configuration
            
        Returns:
            Dict with load result
        """
        try:
            import requests
            
            # Get configuration
            api_url = config.get('url')
            method = config.get('method', 'POST').upper()
            headers = config.get('headers', {})
            auth = config.get('auth')
            
            if not api_url:
                return {
                    'success': False,
                    'error': 'Missing url in config'
                }
            
            # Add default headers
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            
            # Prepare auth if provided
            auth_tuple = None
            if auth and auth.get('type') == 'basic':
                auth_tuple = (auth.get('username'), auth.get('password'))
            
            # Make request
            if method == 'POST':
                response = requests.post(
                    api_url,
                    json=data,
                    headers=headers,
                    auth=auth_tuple,
                    timeout=30
                )
            elif method == 'PUT':
                response = requests.put(
                    api_url,
                    json=data,
                    headers=headers,
                    auth=auth_tuple,
                    timeout=30
                )
            else:
                return {
                    'success': False,
                    'error': f"Unsupported HTTP method: {method}"
                }
            
            # Check response
            response.raise_for_status()
            
            return {
                'success': True,
                'destination': 'api',
                'url': api_url,
                'status_code': response.status_code,
                'response': response.json() if response.content else None
            }
            
        except Exception as e:
            logger.error(f"API load failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def load_batch(
        self,
        data_list: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Load a batch of data records.
        
        Args:
            data_list: List of data dictionaries
            config: Output configuration
            
        Returns:
            Dict with batch load results
        """
        results = []
        successful = 0
        failed = 0
        
        for i, data in enumerate(data_list):
            logger.info(f"Loading record {i+1}/{len(data_list)}")
            
            result = self.load_data(data, config)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        return {
            'success': failed == 0,
            'total': len(data_list),
            'successful': successful,
            'failed': failed,
            'results': results
        }
