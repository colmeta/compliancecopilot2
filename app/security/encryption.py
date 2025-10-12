# ==============================================================================
# app/security/encryption.py
# Enterprise Encryption System - The Data Fortress
# ==============================================================================
"""
This module provides enterprise-grade encryption for CLARITY.
Includes data encryption, key management, and encryption key rotation.
"""

import logging
import secrets
import base64
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from app.models import User, AuditLog
from app import db

logger = logging.getLogger(__name__)

# ==============================================================================
# ENCRYPTION MANAGER
# ==============================================================================

class EncryptionManager:
    """
    Enterprise-grade encryption manager for data protection.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._encryption_keys = {}
        self._load_encryption_keys()
    
    def _load_encryption_keys(self):
        """Load encryption keys from configuration or generate new ones."""
        try:
            # In production, these would be loaded from secure key management
            # For now, we'll use environment variables or generate them
            from config import Config
            
            # Get or generate master key
            master_key = getattr(Config, 'ENCRYPTION_MASTER_KEY', None)
            if not master_key:
                master_key = Fernet.generate_key()
                self.logger.warning("No master encryption key found, generated new one")
            
            # Get or generate user data key
            user_data_key = getattr(Config, 'ENCRYPTION_USER_DATA_KEY', None)
            if not user_data_key:
                user_data_key = Fernet.generate_key()
                self.logger.warning("No user data encryption key found, generated new one")
            
            # Get or generate document key
            document_key = getattr(Config, 'ENCRYPTION_DOCUMENT_KEY', None)
            if not document_key:
                document_key = Fernet.generate_key()
                self.logger.warning("No document encryption key found, generated new one")
            
            self._encryption_keys = {
                'master': master_key,
                'user_data': user_data_key,
                'documents': document_key
            }
            
            self.logger.info("Encryption keys loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load encryption keys: {e}")
            # Generate fallback keys
            self._encryption_keys = {
                'master': Fernet.generate_key(),
                'user_data': Fernet.generate_key(),
                'documents': Fernet.generate_key()
            }
    
    def encrypt_data(self, data: Union[str, bytes], key_type: str = 'user_data',
                    user_id: int = None) -> Dict[str, Any]:
        """
        Encrypt data using the specified key type.
        
        Args:
            data: Data to encrypt (string or bytes)
            key_type: Type of encryption key to use ('master', 'user_data', 'documents')
            user_id: ID of the user (for audit logging)
            
        Returns:
            Dict with encryption result
        """
        try:
            # Get encryption key
            if key_type not in self._encryption_keys:
                return {'success': False, 'error': f'Unknown key type: {key_type}'}
            
            encryption_key = self._encryption_keys[key_type]
            fernet = Fernet(encryption_key)
            
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Encrypt data
            encrypted_data = fernet.encrypt(data_bytes)
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            # Log encryption event
            if user_id:
                from app.security.audit_logger import log_user_action
                log_user_action(
                    user_id=user_id,
                    action='data_encrypted',
                    resource_type='encryption',
                    details={'key_type': key_type, 'data_size': len(data_bytes)}
                )
            
            self.logger.info(f"Data encrypted successfully using {key_type} key")
            
            return {
                'success': True,
                'encrypted_data': encrypted_b64,
                'key_type': key_type,
                'original_size': len(data_bytes),
                'encrypted_size': len(encrypted_b64)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            return {'success': False, 'error': str(e)}
    
    def decrypt_data(self, encrypted_data: str, key_type: str = 'user_data',
                    user_id: int = None) -> Dict[str, Any]:
        """
        Decrypt data using the specified key type.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            key_type: Type of encryption key to use
            user_id: ID of the user (for audit logging)
            
        Returns:
            Dict with decryption result
        """
        try:
            # Get encryption key
            if key_type not in self._encryption_keys:
                return {'success': False, 'error': f'Unknown key type: {key_type}'}
            
            encryption_key = self._encryption_keys[key_type]
            fernet = Fernet(encryption_key)
            
            # Decode base64 and decrypt
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            
            # Try to decode as string, fallback to bytes
            try:
                decrypted_data = decrypted_bytes.decode('utf-8')
            except UnicodeDecodeError:
                decrypted_data = decrypted_bytes
            
            # Log decryption event
            if user_id:
                from app.security.audit_logger import log_user_action
                log_user_action(
                    user_id=user_id,
                    action='data_decrypted',
                    resource_type='encryption',
                    details={'key_type': key_type, 'data_size': len(decrypted_bytes)}
                )
            
            self.logger.info(f"Data decrypted successfully using {key_type} key")
            
            return {
                'success': True,
                'decrypted_data': decrypted_data,
                'key_type': key_type,
                'data_size': len(decrypted_bytes)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_encryption_key(self, key_type: str = 'custom') -> Dict[str, Any]:
        """
        Generate a new encryption key.
        
        Args:
            key_type: Type of key to generate
            
        Returns:
            Dict with key generation result
        """
        try:
            # Generate new key
            new_key = Fernet.generate_key()
            key_b64 = base64.b64encode(new_key).decode('utf-8')
            
            # Store key (in production, this would be stored securely)
            self._encryption_keys[key_type] = new_key
            
            self.logger.info(f"New encryption key generated for type: {key_type}")
            
            return {
                'success': True,
                'key_type': key_type,
                'key': key_b64,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate encryption key: {e}")
            return {'success': False, 'error': str(e)}
    
    def rotate_encryption_key(self, key_type: str, user_id: int = None) -> Dict[str, Any]:
        """
        Rotate an encryption key (generate new key and mark old one for retirement).
        
        Args:
            key_type: Type of key to rotate
            user_id: ID of the user performing the rotation
            
        Returns:
            Dict with key rotation result
        """
        try:
            if key_type not in self._encryption_keys:
                return {'success': False, 'error': f'Key type {key_type} not found'}
            
            # Generate new key
            new_key = Fernet.generate_key()
            old_key = self._encryption_keys[key_type]
            
            # Store old key for decryption of existing data
            old_key_id = f"{key_type}_old_{int(datetime.utcnow().timestamp())}"
            self._encryption_keys[old_key_id] = old_key
            
            # Replace with new key
            self._encryption_keys[key_type] = new_key
            
            # Log key rotation
            if user_id:
                from app.security.audit_logger import log_user_action
                log_user_action(
                    user_id=user_id,
                    action='encryption_key_rotated',
                    resource_type='encryption',
                    details={'key_type': key_type, 'old_key_id': old_key_id}
                )
            
            self.logger.info(f"Encryption key rotated for type: {key_type}")
            
            return {
                'success': True,
                'key_type': key_type,
                'old_key_id': old_key_id,
                'rotated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to rotate encryption key: {e}")
            return {'success': False, 'error': str(e)}
    
    def encrypt_user_data(self, user_id: int, data: Union[str, bytes]) -> Dict[str, Any]:
        """
        Encrypt user-specific data.
        
        Args:
            user_id: ID of the user
            data: Data to encrypt
            
        Returns:
            Dict with encryption result
        """
        return self.encrypt_data(data, 'user_data', user_id)
    
    def decrypt_user_data(self, user_id: int, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt user-specific data.
        
        Args:
            user_id: ID of the user
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Dict with decryption result
        """
        return self.decrypt_data(encrypted_data, 'user_data', user_id)
    
    def encrypt_document(self, user_id: int, document_data: Union[str, bytes]) -> Dict[str, Any]:
        """
        Encrypt document data.
        
        Args:
            user_id: ID of the user
            document_data: Document data to encrypt
            
        Returns:
            Dict with encryption result
        """
        return self.encrypt_data(document_data, 'documents', user_id)
    
    def decrypt_document(self, user_id: int, encrypted_document: str) -> Dict[str, Any]:
        """
        Decrypt document data.
        
        Args:
            user_id: ID of the user
            encrypted_document: Encrypted document to decrypt
            
        Returns:
            Dict with decryption result
        """
        return self.decrypt_data(encrypted_document, 'documents', user_id)
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """
        Get current encryption status and key information.
        
        Returns:
            Dict with encryption status
        """
        try:
            key_info = {}
            for key_type, key in self._encryption_keys.items():
                key_info[key_type] = {
                    'available': True,
                    'key_id': base64.b64encode(key[:8]).decode('utf-8')  # First 8 bytes as ID
                }
            
            return {
                'success': True,
                'encryption_enabled': True,
                'available_keys': list(self._encryption_keys.keys()),
                'key_info': key_info,
                'status': 'operational'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get encryption status: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_encryption_integrity(self) -> Dict[str, Any]:
        """
        Validate encryption system integrity.
        
        Returns:
            Dict with validation result
        """
        try:
            # Test encryption/decryption with each key
            test_data = "CLARITY encryption integrity test"
            validation_results = {}
            
            for key_type in self._encryption_keys:
                # Encrypt test data
                encrypt_result = self.encrypt_data(test_data, key_type)
                if not encrypt_result['success']:
                    validation_results[key_type] = {'status': 'failed', 'error': encrypt_result['error']}
                    continue
                
                # Decrypt test data
                decrypt_result = self.decrypt_data(encrypt_result['encrypted_data'], key_type)
                if not decrypt_result['success']:
                    validation_results[key_type] = {'status': 'failed', 'error': decrypt_result['error']}
                    continue
                
                # Verify data integrity
                if decrypt_result['decrypted_data'] == test_data:
                    validation_results[key_type] = {'status': 'passed', 'integrity': True}
                else:
                    validation_results[key_type] = {'status': 'failed', 'error': 'Data integrity check failed'}
            
            # Overall status
            all_passed = all(result['status'] == 'passed' for result in validation_results.values())
            
            return {
                'success': True,
                'overall_status': 'passed' if all_passed else 'failed',
                'validation_results': validation_results,
                'tested_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate encryption integrity: {e}")
            return {'success': False, 'error': str(e)}

# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def encrypt_data(data: Union[str, bytes], key_type: str = 'user_data', user_id: int = None) -> Dict[str, Any]:
    """Encrypt data using the encryption manager."""
    manager = EncryptionManager()
    return manager.encrypt_data(data, key_type, user_id)

def decrypt_data(encrypted_data: str, key_type: str = 'user_data', user_id: int = None) -> Dict[str, Any]:
    """Decrypt data using the encryption manager."""
    manager = EncryptionManager()
    return manager.decrypt_data(encrypted_data, key_type, user_id)

def generate_encryption_key(key_type: str = 'custom') -> Dict[str, Any]:
    """Generate a new encryption key."""
    manager = EncryptionManager()
    return manager.generate_encryption_key(key_type)

def rotate_encryption_key(key_type: str, user_id: int = None) -> Dict[str, Any]:
    """Rotate an encryption key."""
    manager = EncryptionManager()
    return manager.rotate_encryption_key(key_type, user_id)

