# ==============================================================================
# email_service.py
# CLARITY Email Delivery System - Prevents browser crashes, enables scalability
# ==============================================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Handles all email notifications for CLARITY Engine.
    
    WHY EMAIL DELIVERY?
    - Prevents browser timeouts for long-running tasks
    - Handles infinite concurrent users without crashes
    - Users can close browser and get results via email
    - Professional user experience
    """
    
    def __init__(self):
        self.enabled = os.getenv('ENABLE_EMAIL_DELIVERY', 'true').lower() == 'true'
        self.mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.mail_port = int(os.getenv('MAIL_PORT', '587'))
        self.mail_username = os.getenv('MAIL_USERNAME')
        self.mail_password = os.getenv('MAIL_PASSWORD')
        self.mail_sender = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@claritypearl.com')
        
        if not self.enabled:
            logger.warning("Email delivery is DISABLED. Set ENABLE_EMAIL_DELIVERY=true to enable.")
        elif not self.mail_username or not self.mail_password:
            logger.warning("Email credentials not configured. Emails will NOT be sent.")
            self.enabled = False
    
    def send_analysis_complete(self, 
                               user_email: str, 
                               analysis_id: str,
                               domain: str,
                               result_summary: str,
                               confidence_score: float,
                               download_url: Optional[str] = None) -> bool:
        """
        Send email notification when analysis is complete.
        
        Args:
            user_email: User's email address
            analysis_id: Unique analysis ID
            domain: Domain accelerator used (e.g., "Legal Intelligence")
            result_summary: Brief summary of results
            confidence_score: AI confidence score (0-1)
            download_url: Optional URL to download full results
        """
        if not self.enabled:
            logger.info(f"Email delivery disabled. Would have sent to {user_email}")
            return False
        
        subject = f"✅ CLARITY Analysis Complete - {domain}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); border-radius: 10px;">
                <h1 style="color: #fbbf24; margin: 0;">CLARITY Engine</h1>
                <p style="color: #e2e8f0; margin: 5px 0 20px 0;">by Clarity Pearl</p>
            </div>
            
            <div style="max-width: 600px; margin: 20px auto; padding: 30px; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #1e3a8a; margin-top: 0;">Your Analysis is Ready! 🎉</h2>
                
                <div style="background: #f0f9ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Domain:</strong> {domain}</p>
                    <p style="margin: 5px 0;"><strong>Analysis ID:</strong> {analysis_id}</p>
                    <p style="margin: 5px 0;"><strong>Confidence Score:</strong> {int(confidence_score * 100)}%</p>
                </div>
                
                <h3 style="color: #1e3a8a;">Summary:</h3>
                <p style="background: #f8fafc; padding: 15px; border-radius: 5px;">{result_summary}</p>
                
                {f'<a href="{download_url}" style="display: inline-block; background: #fbbf24; color: #1e3a8a; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0;">Download Full Results</a>' if download_url else ''}
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #64748b; font-size: 14px; margin: 5px 0;">
                        Questions? Contact us:<br>
                        📧 nsubugacollin@gmail.com<br>
                        📱 +256 705 885 118
                    </p>
                    <p style="color: #94a3b8; font-size: 12px; margin-top: 15px;">
                        © 2025 Clarity Pearl. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_funding_package_complete(self,
                                     user_email: str,
                                     project_name: str,
                                     funding_level: str,
                                     document_count: int,
                                     download_url: str) -> bool:
        """
        Send email notification when Funding Engine package is complete.
        """
        if not self.enabled:
            return False
        
        subject = f"🎉 Your Funding Package is Ready - {project_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 10px;">
                <h1 style="color: #fbbf24; margin: 0;">🎉 Funding Package Ready!</h1>
                <p style="color: #e2e8f0; margin: 5px 0 20px 0;">CLARITY Funding Readiness Engine</p>
            </div>
            
            <div style="max-width: 600px; margin: 20px auto; padding: 30px; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #059669; margin-top: 0;">Your {funding_level} Funding Package</h2>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    We've generated <strong>{document_count} professional documents</strong> for <strong>{project_name}</strong>.
                </p>
                
                <div style="background: #d1fae5; padding: 20px; border-left: 4px solid #10b981; margin: 20px 0;">
                    <p style="margin: 5px 0; font-size: 18px; font-weight: bold; color: #065f46;">
                        ✅ Presidential-Grade Quality
                    </p>
                    <p style="margin: 5px 0; color: #047857;">
                        ✅ Deep Research & Analysis<br>
                        ✅ Human Touch Writing<br>
                        ✅ Y-Combinator Standard<br>
                        ✅ Fortune 50 Ready
                    </p>
                </div>
                
                <a href="{download_url}" style="display: inline-block; background: #fbbf24; color: #1e3a8a; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 18px; margin: 20px 0;">
                    Download Your Package 📦
                </a>
                
                <h3 style="color: #059669; margin-top: 30px;">Next Steps:</h3>
                <ol style="color: #475569;">
                    <li>Review each document and customize with your specific details</li>
                    <li>Have your team provide feedback</li>
                    <li>Schedule meetings with investors or funding partners</li>
                    <li>Update documents as you gain traction</li>
                </ol>
                
                <div style="margin-top: 30px; padding: 20px; background: #fef3c7; border-radius: 5px;">
                    <p style="margin: 0; color: #92400e;">
                        <strong>💡 Pro Tip:</strong> Need refinements? Reply to this email with your feedback, 
                        and we'll regenerate specific documents with your changes.
                    </p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #64748b; font-size: 14px; margin: 5px 0;">
                        Questions? Contact us:<br>
                        📧 nsubugacollin@gmail.com<br>
                        📱 +256 705 885 118
                    </p>
                    <p style="color: #94a3b8; font-size: 12px; margin-top: 15px;">
                        © 2025 Clarity Pearl. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_task_submitted(self,
                            user_email: str,
                            task_type: str,
                            estimated_time: str) -> bool:
        """
        Send immediate confirmation that task was submitted.
        """
        if not self.enabled:
            return False
        
        subject = "✅ CLARITY Task Submitted - Check Your Email"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 30px; background: #ffffff; border-radius: 10px;">
                <h2 style="color: #3b82f6;">Your Task is Being Processed 🚀</h2>
                
                <p style="font-size: 16px;">
                    <strong>{task_type}</strong> task submitted successfully!
                </p>
                
                <div style="background: #dbeafe; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Estimated Time:</strong> {estimated_time}</p>
                    <p style="margin: 5px 0;">You can <strong>close this browser</strong>. We'll email you when it's ready.</p>
                </div>
                
                <p style="color: #64748b;">
                    CLARITY is working on your request in the background. You'll receive another email 
                    with your results as soon as it's complete.
                </p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #94a3b8; font-size: 12px;">
                        © 2025 Clarity Pearl • nsubugacollin@gmail.com • +256 705 885 118
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_funding_package_email(self, 
                                   to_email: str,
                                   company_name: str,
                                   documents: List[dict],
                                   zip_path: str,
                                   download_url: Optional[str] = None,
                                   package_size_mb: float = 0) -> bool:
        """
        Send email with funding package (20 documents, Presidential quality)
        Includes download link or attachment
        """
        if not self.enabled:
            return False
        
        doc_count = len(documents)
        total_pages = sum(doc.get('pages', 0) for doc in documents)
        
        subject = f"🎉 Your Funding Package is Ready - {company_name}"
        
        # Generate document list HTML
        docs_by_category = {}
        for doc in documents:
            category = doc.get('category', 'other')
            if category not in docs_by_category:
                docs_by_category[category] = []
            docs_by_category[category].append(doc)
        
        docs_html = ""
        for category, cat_docs in docs_by_category.items():
            docs_html += f'<h4 style="color: #F59E0B; margin-top: 15px;">{category.upper()}</h4><ul style="margin: 5px 0;">'
            for doc in cat_docs:
                docs_html += f'<li>{doc["name"]} ({doc.get("pages", "?")} pages)</li>'
            docs_html += '</ul>'
        
        download_section = ""
        if download_url:
            download_section = f"""
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{download_url}" 
                       style="display: inline-block; padding: 15px 40px; background: #F59E0B; 
                              color: white; text-decoration: none; border-radius: 8px; 
                              font-weight: bold; font-size: 18px;">
                        📦 DOWNLOAD YOUR PACKAGE ({package_size_mb} MB)
                    </a>
                    <p style="color: #94a3b8; font-size: 12px; margin-top: 10px;">
                        Link expires in 7 days
                    </p>
                </div>
            """
        else:
            download_section = f"""
                <div style="background: #dbeafe; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                    <p style="margin: 0;">
                        <strong>📎 Package attached to this email</strong> ({package_size_mb} MB ZIP file)
                    </p>
                </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f8fafc;">
            <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">
                        🎉 Your Funding Package is Ready!
                    </h1>
                    <p style="color: #CBD5E1; margin: 10px 0 0 0; font-size: 16px;">
                        Presidential-Grade Documentation • Fortune 50 Quality
                    </p>
                </div>
                
                <!-- Body -->
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #1E293B;">
                        Hello <strong>{company_name}</strong> team! 👋
                    </p>
                    
                    <p style="font-size: 16px; color: #475569;">
                        Your complete funding documentation package has been generated and is ready for download.
                    </p>
                    
                    <!-- Package Stats -->
                    <div style="background: #F0FDF4; border-left: 4px solid #22C55E; padding: 20px; margin: 25px 0;">
                        <h3 style="margin: 0 0 15px 0; color: #166534;">📊 Package Contents</h3>
                        <div style="display: flex; justify-content: space-around; text-align: center;">
                            <div>
                                <p style="margin: 0; font-size: 32px; font-weight: bold; color: #F59E0B;">{doc_count}</p>
                                <p style="margin: 5px 0 0 0; font-size: 14px; color: #64748b;">Documents</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 32px; font-weight: bold; color: #F59E0B;">{total_pages}+</p>
                                <p style="margin: 5px 0 0 0; font-size: 14px; color: #64748b;">Pages</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 32px; font-weight: bold; color: #F59E0B;">3</p>
                                <p style="margin: 5px 0 0 0; font-size: 14px; color: #64748b;">Formats</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Download Button or Attachment Notice -->
                    {download_section}
                    
                    <!-- Document List -->
                    <div style="margin: 25px 0;">
                        <h3 style="color: #1E293B; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px;">
                            📋 Documents Included
                        </h3>
                        {docs_html}
                    </div>
                    
                    <!-- Formats -->
                    <div style="background: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 25px 0;">
                        <h4 style="margin: 0 0 10px 0; color: #92400E;">📄 File Formats</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #78350F;">
                            <li><strong>PDF</strong> - For professional presentation and printing</li>
                            <li><strong>Word (.docx)</strong> - Fully editable for customization</li>
                            <li><strong>PowerPoint (.pptx)</strong> - For pitch deck presentations</li>
                        </ul>
                    </div>
                    
                    <!-- Quality Badge -->
                    <div style="text-align: center; margin: 30px 0; padding: 20px; background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); border-radius: 12px;">
                        <h3 style="color: white; margin: 0 0 5px 0;">✨ Presidential Quality Standard</h3>
                        <p style="color: white; margin: 0; opacity: 0.9;">
                            Fortune 50 • Y-Combinator • Top-Tier VCs
                        </p>
                    </div>
                    
                    <!-- Next Steps -->
                    <div style="margin: 25px 0;">
                        <h3 style="color: #1E293B;">🚀 Next Steps</h3>
                        <ol style="color: #475569; line-height: 1.8;">
                            <li>Download and review all documents</li>
                            <li>Customize Word documents as needed</li>
                            <li>Use PDF versions for investor presentations</li>
                            <li>Practice your pitch deck presentation</li>
                            <li>Get feedback from advisors and mentors</li>
                            <li>Start reaching out to investors!</li>
                        </ol>
                    </div>
                    
                    <!-- Support -->
                    <div style="background: #F1F5F9; padding: 15px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; color: #475569; font-size: 14px;">
                            <strong>Need help?</strong> We're here to support you!<br>
                            📧 nsubugacollin@gmail.com<br>
                            📱 +256 705 885 118
                        </p>
                    </div>
                    
                    <p style="color: #64748b; font-size: 14px; margin-top: 30px;">
                        Good luck with your fundraising! We're excited to see what you build. 💪
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="background: #F8FAFC; padding: 20px; text-align: center; border-top: 1px solid #E2E8F0;">
                    <p style="color: #94A3B8; font-size: 12px; margin: 0;">
                        © 2025 Clarity Pearl • CLARITY Funding Engine<br>
                        Presidential-Grade Funding Documentation
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send with or without attachment
        return self._send_email_with_attachment(to_email, subject, html_body, zip_path)
    
    def _send_email_with_attachment(self, to_email: str, subject: str, html_body: str, 
                                    attachment_path: Optional[str] = None) -> bool:
        """
        Send email with optional ZIP attachment
        """
        if not self.enabled:
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.mail_sender
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Attachment (if file exists and is not too large)
            if attachment_path and os.path.exists(attachment_path):
                file_size_mb = os.path.getsize(attachment_path) / (1024 * 1024)
                
                # Only attach if < 25MB (Gmail limit)
                if file_size_mb < 25:
                    with open(attachment_path, 'rb') as f:
                        attachment = MIMEBase('application', 'zip')
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(attachment_path)}'
                        )
                        msg.attach(attachment)
                        logger.info(f"📎 Attached file: {file_size_mb:.2f} MB")
                else:
                    logger.warning(f"⚠️  File too large for email attachment: {file_size_mb:.2f} MB")
            
            # Send
            server = smtplib.SMTP(self.mail_server, self.mail_port)
            server.starttls()
            server.login(self.mail_username, self.mail_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Funding package email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send funding package email to {to_email}: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return self.enabled and bool(self.mail_username) and bool(self.mail_password)
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Internal method to send email via SMTP.
        """
        if not self.enabled:
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.mail_sender
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(self.mail_server, self.mail_port)
            server.starttls()
            server.login(self.mail_username, self.mail_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False

# Global email service instance
email_service = EmailService()

# Convenience functions
def send_analysis_complete(*args, **kwargs):
    return email_service.send_analysis_complete(*args, **kwargs)

def send_funding_package_complete(*args, **kwargs):
    return email_service.send_funding_package_complete(*args, **kwargs)

def send_task_submitted(*args, **kwargs):
    return email_service.send_task_submitted(*args, **kwargs)
