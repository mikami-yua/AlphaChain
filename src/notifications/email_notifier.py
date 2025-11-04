"""
Email notification module for sending emails via 163 SMTP server
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Optional
from loguru import logger


def create_email_notifier_from_config(config) -> Optional['EmailNotifier']:
    """
    Create EmailNotifier instance from configuration object
    
    Args:
        config: Configuration object with email settings
        
    Returns:
        EmailNotifier instance if email is enabled, None otherwise
    """
    if not getattr(config, 'email_enabled', False):
        logger.warning("Email notification is disabled in configuration")
        return None

    sender = getattr(config, 'email_sender', None)
    password = getattr(config, 'email_password', None)

    if not sender or not password:
        logger.error("Email sender or password not configured")
        return None

    sender_name = getattr(config, 'email_sender_name', None)
    use_ssl = getattr(config, 'email_use_ssl', True)

    return EmailNotifier(
        sender_email=sender,
        sender_password=password,
        sender_name=sender_name,
        use_ssl=use_ssl
    )


class EmailNotifier:
    """
    Email notification service using 163 SMTP server
    
    This module provides a simple interface for sending emails
    through 163 email service. It supports both plain text and HTML emails.
    """

    # 163 SMTP server configuration
    SMTP_SERVER = "smtp.163.com"
    SMTP_PORT = 465  # SSL port
    SMTP_PORT_ALT = 25  # Alternative non-SSL port

    def __init__(
            self,
            sender_email: str,
            sender_password: str,
            sender_name: Optional[str] = None,
            use_ssl: bool = True
    ):
        """
        Initialize email notifier
        
        Args:
            sender_email: 163 email address (e.g., 'yourname@163.com')
            sender_password: Email password or authorization code (for 163, use authorization code)
            sender_name: Display name for sender (optional)
            use_ssl: Whether to use SSL connection (default: True)
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.sender_name = sender_name or sender_email.split('@')[0]
        self.use_ssl = use_ssl
        self.smtp_port = self.SMTP_PORT if use_ssl else self.SMTP_PORT_ALT

    def _create_message(
            self,
            recipient: str,
            subject: str,
            body: str,
            is_html: bool = False,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None
    ) -> MIMEMultipart:
        """
        Create email message
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML format
            cc: CC recipients list (optional)
            bcc: BCC recipients list (optional)
            
        Returns:
            MIMEMultipart message object
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = Header(f"{self.sender_name} <{self.sender_email}>", 'utf-8')
        msg['To'] = Header(recipient, 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')

        if cc:
            msg['Cc'] = ', '.join(cc)

        # Add body content
        content_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, content_type, 'utf-8'))

        return msg

    def send_email(
            self,
            recipient: str,
            subject: str,
            body: str,
            is_html: bool = False,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send email to single recipient
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML format
            cc: CC recipients list (optional)
            bcc: BCC recipients list (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = self._create_message(recipient, subject, body, is_html, cc, bcc)

            # Prepare recipients list
            recipients = [recipient]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # Connect to SMTP server and send
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.SMTP_SERVER, self.smtp_port)
            else:
                server = smtplib.SMTP(self.SMTP_SERVER, self.smtp_port)
                server.starttls()

            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipients, msg.as_string())
            server.quit()

            logger.info(f"Email sent successfully to {recipient}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_bulk_email(
            self,
            recipients: List[str],
            subject: str,
            body: str,
            is_html: bool = False
    ) -> dict:
        """
        Send email to multiple recipients
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML format
            
        Returns:
            Dictionary with success/failure status for each recipient
        """
        results = {}
        for recipient in recipients:
            success = self.send_email(recipient, subject, body, is_html)
            results[recipient] = success
        return results

    def send_html_email(
            self,
            recipient: str,
            subject: str,
            html_body: str,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send HTML email (convenience method)
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            html_body: HTML email body content
            cc: CC recipients list (optional)
            bcc: BCC recipients list (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        return self.send_email(recipient, subject, html_body, is_html=True, cc=cc, bcc=bcc)

    def send_text_email(
            self,
            recipient: str,
            subject: str,
            text_body: str,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send plain text email (convenience method)
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            text_body: Plain text email body content
            cc: CC recipients list (optional)
            bcc: BCC recipients list (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        return self.send_email(recipient, subject, text_body, is_html=False, cc=cc, bcc=bcc)
