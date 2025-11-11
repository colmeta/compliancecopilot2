"""
CLARITY Funding Engine - Package Manager
Handles ZIP packaging and cloud storage for document packages
"""

import os
import zipfile
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# boto3 is optional (for cloud storage)
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logging.warning("boto3 not installed - S3 upload disabled (local storage only)")

logger = logging.getLogger(__name__)


class PackageManager:
    """Manage document packaging and cloud storage"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'clarity-funding-documents')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize S3 if boto3 available AND credentials provided
        if not BOTO3_AVAILABLE:
            logger.info("boto3 not available - using local storage only")
            return
        
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if aws_key and aws_secret:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_key,
                    aws_secret_access_key=aws_secret,
                    region_name=self.aws_region
                )
                logger.info("S3 client initialized successfully")
            except Exception as e:
                logger.warning(f"S3 initialization failed (will use local storage): {e}")
        else:
            logger.info("AWS credentials not found - using local storage only")
    
    def create_zip_package(self, file_paths: Dict[str, str], output_path: str, 
                          package_name: str = "funding_package") -> str:
        """
        Create a ZIP file containing all documents
        
        Args:
            file_paths: Dict of {document_id: file_path}
            output_path: Path for the ZIP file
            package_name: Base name for the package
        
        Returns:
            Path to the created ZIP file
        """
        try:
            zip_filename = f"{package_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(output_path, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for doc_id, file_path in file_paths.items():
                    if os.path.exists(file_path):
                        # Add file to ZIP with organized folder structure
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
                        logger.info(f"Added to ZIP: {arcname}")
                
                # Add README
                readme_content = self._generate_readme(file_paths)
                zipf.writestr('README.txt', readme_content)
            
            logger.info(f"ZIP package created: {zip_path} ({len(file_paths)} documents)")
            return zip_path
            
        except Exception as e:
            logger.error(f"ZIP creation failed: {e}")
            raise
    
    def upload_to_s3(self, file_path: str, object_key: str = None, 
                     expiration: int = 7) -> Optional[str]:
        """
        Upload file to S3 and generate presigned URL
        
        Args:
            file_path: Path to file to upload
            object_key: S3 object key (default: filename)
            expiration: URL expiration in days
        
        Returns:
            Presigned URL or None if S3 not available
        """
        if not self.s3_client:
            logger.warning("S3 not available - skipping upload")
            return None
        
        try:
            if object_key is None:
                object_key = os.path.basename(file_path)
            
            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(file_path),
                    'ContentDisposition': f'attachment; filename="{os.path.basename(file_path)}"'
                }
            )
            
            # Generate presigned URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration * 86400  # Convert days to seconds
            )
            
            logger.info(f"File uploaded to S3: {object_key}")
            return url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return None
    
    def package_and_upload(self, file_paths: Dict[str, str], temp_dir: str,
                          company_name: str = "company") -> Dict:
        """
        Complete packaging workflow: ZIP + upload + generate URLs
        
        Args:
            file_paths: Dict of {document_id: file_path}
            temp_dir: Temporary directory for ZIP
            company_name: Company name for package naming
        
        Returns:
            Dict with package info and download URL
        """
        try:
            # Sanitize company name for filename
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).strip()
            safe_company_name = safe_company_name.replace(' ', '_')
            package_name = f"{safe_company_name}_funding_package"
            
            # Create ZIP
            zip_path = self.create_zip_package(file_paths, temp_dir, package_name)
            zip_size = os.path.getsize(zip_path)
            
            # Upload to S3 (if available)
            download_url = None
            if self.s3_client:
                s3_key = f"packages/{package_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                download_url = self.upload_to_s3(zip_path, s3_key, expiration=7)
            
            return {
                'success': True,
                'zip_path': zip_path,
                'zip_filename': os.path.basename(zip_path),
                'zip_size_mb': round(zip_size / (1024 * 1024), 2),
                'document_count': len(file_paths),
                'download_url': download_url,
                'storage': 's3' if download_url else 'local',
                'expires_in_days': 7 if download_url else None,
                'message': 'Package created and uploaded to cloud storage' if download_url 
                          else 'Package created (local storage - S3 not configured)'
            }
            
        except Exception as e:
            logger.error(f"Package creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create package'
            }
    
    def _generate_readme(self, file_paths: Dict[str, str]) -> str:
        """Generate README content for the package"""
        readme = f"""
========================================
CLARITY FUNDING PACKAGE
========================================

Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Document Count: {len(file_paths)}

This package contains your complete funding documentation generated by the CLARITY Funding Engine.

DOCUMENTS INCLUDED:
-------------------
"""
        for idx, (doc_id, file_path) in enumerate(file_paths.items(), 1):
            filename = os.path.basename(file_path)
            readme += f"{idx}. {filename}\n"
        
        readme += """
DOCUMENT FORMATS:
-----------------
- PDF: For printing and professional presentation
- Word (.docx): For editing and customization
- PowerPoint (.pptx): For presentations (Pitch Deck only)

USAGE INSTRUCTIONS:
-------------------
1. Review all documents for accuracy
2. Customize as needed (Word documents are editable)
3. Use PDF versions for investor presentations
4. Keep this package secure (contains confidential information)

SUPPORT:
--------
Company: Clarity Pearl
Email: nsubugacollin@gmail.com
Phone: +256705885118

For questions or support, please contact us.

========================================
© Clarity Pearl - CLARITY Funding Engine
Presidential-Grade Funding Documentation
========================================
"""
        return readme
    
    def _get_content_type(self, file_path: str) -> str:
        """Get MIME type for file"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.zip': 'application/zip'
        }
        return content_types.get(ext, 'application/octet-stream')


# Singleton
_package_manager = None

def get_package_manager():
    """Get singleton package manager instance"""
    global _package_manager
    if _package_manager is None:
        _package_manager = PackageManager()
    return _package_manager
