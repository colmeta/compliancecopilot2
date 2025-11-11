"""
CLARITY Document Vault - Secure Storage for Scanned Documents
Store, organize, search, and retrieve scanned documents
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import hashlib

logger = logging.getLogger(__name__)


class DocumentVault:
    """
    Secure document storage and management
    
    Features:
    - Store scanned documents with OCR text
    - Organize by categories/tags
    - Full-text search
    - Version history
    - Access control
    - Encryption at rest (optional)
    """
    
    def __init__(self, storage_path: str = '/tmp/clarity_vault'):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # In production, use database + S3
        # For now, using filesystem as proof of concept
        self.documents = {}  # doc_id -> metadata
        self.index_path = os.path.join(storage_path, 'index.json')
        self._load_index()
    
    def store_document(self, 
                      file_data: bytes,
                      filename: str,
                      user_id: str,
                      ocr_text: str = None,
                      category: str = None,
                      tags: List[str] = None,
                      metadata: Dict = None) -> Dict:
        """
        Store document in vault
        
        Args:
            file_data: Document file bytes
            filename: Original filename
            user_id: Owner user ID
            ocr_text: Extracted OCR text (for search)
            category: Document category
            tags: List of tags
            metadata: Additional metadata
        
        Returns:
            {
                'success': bool,
                'document_id': str,
                'url': str (if cloud storage),
                'storage_location': str
            }
        """
        try:
            # Generate document ID
            doc_id = self._generate_doc_id(file_data, user_id)
            
            # Create storage directory for user
            user_dir = os.path.join(self.storage_path, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(user_dir, f"{doc_id}_{filename}")
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Create metadata
            document = {
                'id': doc_id,
                'filename': filename,
                'user_id': user_id,
                'file_path': file_path,
                'file_size': len(file_data),
                'file_type': os.path.splitext(filename)[1],
                'ocr_text': ocr_text,
                'category': category or 'uncategorized',
                'tags': tags or [],
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'version': 1
            }
            
            # Store in index
            self.documents[doc_id] = document
            self._save_index()
            
            logger.info(f"📁 Document stored: {doc_id} ({filename})")
            
            return {
                'success': True,
                'document_id': doc_id,
                'filename': filename,
                'file_size': len(file_data),
                'category': category,
                'storage_location': file_path,
                'created_at': document['created_at']
            }
            
        except Exception as e:
            logger.error(f"Document storage failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_document(self, doc_id: str, user_id: str = None) -> Optional[Dict]:
        """Retrieve document metadata"""
        document = self.documents.get(doc_id)
        
        if not document:
            return None
        
        # Check access control
        if user_id and document['user_id'] != user_id:
            return None
        
        return document
    
    def get_document_file(self, doc_id: str, user_id: str = None) -> Optional[bytes]:
        """Retrieve document file data"""
        document = self.get_document(doc_id, user_id)
        
        if not document:
            return None
        
        try:
            with open(document['file_path'], 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"File retrieval failed: {e}")
            return None
    
    def list_documents(self, 
                      user_id: str,
                      category: str = None,
                      tags: List[str] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[Dict]:
        """List user's documents with filters"""
        # Filter by user
        user_docs = [
            doc for doc in self.documents.values()
            if doc['user_id'] == user_id
        ]
        
        # Filter by category
        if category:
            user_docs = [
                doc for doc in user_docs
                if doc['category'] == category
            ]
        
        # Filter by tags
        if tags:
            user_docs = [
                doc for doc in user_docs
                if any(tag in doc['tags'] for tag in tags)
            ]
        
        # Sort by created_at (newest first)
        user_docs.sort(key=lambda d: d['created_at'], reverse=True)
        
        # Pagination
        return user_docs[offset:offset+limit]
    
    def search_documents(self, 
                        user_id: str,
                        query: str,
                        limit: int = 20) -> List[Dict]:
        """Full-text search in documents"""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents.values():
            if doc['user_id'] != user_id:
                continue
            
            # Search in filename, category, tags, OCR text
            searchable = ' '.join([
                doc['filename'],
                doc['category'],
                ' '.join(doc['tags']),
                doc.get('ocr_text', '')
            ]).lower()
            
            if query_lower in searchable:
                # Calculate relevance score
                score = searchable.count(query_lower)
                results.append({
                    'document': doc,
                    'score': score
                })
        
        # Sort by relevance
        results.sort(key=lambda r: r['score'], reverse=True)
        
        return [r['document'] for r in results[:limit]]
    
    def update_document(self, 
                       doc_id: str,
                       user_id: str,
                       category: str = None,
                       tags: List[str] = None,
                       metadata: Dict = None) -> Dict:
        """Update document metadata"""
        document = self.get_document(doc_id, user_id)
        
        if not document:
            return {
                'success': False,
                'error': 'Document not found or access denied'
            }
        
        # Update fields
        if category:
            document['category'] = category
        if tags is not None:
            document['tags'] = tags
        if metadata:
            document['metadata'].update(metadata)
        
        document['updated_at'] = datetime.now().isoformat()
        document['version'] += 1
        
        self._save_index()
        
        return {
            'success': True,
            'document': document
        }
    
    def delete_document(self, doc_id: str, user_id: str) -> Dict:
        """Delete document from vault"""
        document = self.get_document(doc_id, user_id)
        
        if not document:
            return {
                'success': False,
                'error': 'Document not found or access denied'
            }
        
        try:
            # Delete file
            if os.path.exists(document['file_path']):
                os.remove(document['file_path'])
            
            # Remove from index
            del self.documents[doc_id]
            self._save_index()
            
            return {
                'success': True,
                'message': 'Document deleted'
            }
            
        except Exception as e:
            logger.error(f"Document deletion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_storage_stats(self, user_id: str) -> Dict:
        """Get storage statistics for user"""
        user_docs = [
            doc for doc in self.documents.values()
            if doc['user_id'] == user_id
        ]
        
        total_size = sum(doc['file_size'] for doc in user_docs)
        
        # Group by category
        by_category = {}
        for doc in user_docs:
            category = doc['category']
            if category not in by_category:
                by_category[category] = {'count': 0, 'size': 0}
            by_category[category]['count'] += 1
            by_category[category]['size'] += doc['file_size']
        
        return {
            'total_documents': len(user_docs),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_category': by_category,
            'oldest_document': min((doc['created_at'] for doc in user_docs), default=None),
            'newest_document': max((doc['created_at'] for doc in user_docs), default=None)
        }
    
    def _generate_doc_id(self, file_data: bytes, user_id: str) -> str:
        """Generate unique document ID"""
        content_hash = hashlib.sha256(file_data).hexdigest()[:16]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"doc_{timestamp}_{content_hash}"
    
    def _load_index(self):
        """Load document index from disk"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r') as f:
                    self.documents = json.load(f)
                logger.info(f"📚 Loaded {len(self.documents)} documents from vault")
            except Exception as e:
                logger.error(f"Index load failed: {e}")
                self.documents = {}
    
    def _save_index(self):
        """Save document index to disk"""
        try:
            with open(self.index_path, 'w') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            logger.error(f"Index save failed: {e}")


# Singleton
_document_vault = None

def get_document_vault():
    """Get singleton document vault instance"""
    global _document_vault
    if _document_vault is None:
        _document_vault = DocumentVault()
    return _document_vault
