"""Email Sending Service

Handles sending emails with attachments using SMTP.
Provides a pre-configured EmailSender instance for the application.
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate
from pathlib import Path
from app.config import settings
from typing import Optional

class EmailSender:
    """SMTP email sender with attachment support.
    
    Configuration is loaded from environment variables with defaults for Mailtrap.
    
    Attributes:
        smtp_server: SMTP server hostname
        smtp_port: SMTP server port
        smtp_username: SMTP authentication username
        smtp_password: SMTP authentication password
        from_email: Sender email address
    """
    
    def __init__(self):
        """Initialize SMTP configuration with environment defaults."""
        self.smtp_server = os.getenv("SMTP_SERVER", "sandbox.smtp.mailtrap.io")
        self.smtp_port = int(os.getenv("SMTP_PORT", 2525))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "payroll@company.com")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
        cc_emails: Optional[list] = None
    ) -> dict:
        """Send an email with optional attachment.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Plain text email body
            attachment_path: Path to file attachment (optional)
            cc_emails: List of CC email addresses (optional)
            
        Returns:
            dict: Result dictionary with:
                - status: "success" or "failed"
                - message: Result description
                - email: Recipient email address
                
        Example:
            >>> result = email_sender.send_email(
            ...     "user@example.com",
            ...     "Your Paystub",
            ...     "Attached is your paystub",
            ...     "paystub.pdf"
            ... )
            >>> print(result)
            {
                'status': 'success',
                'message': 'Email sent successfully',
                'email': 'user@example.com'
            }
        """
        try:
            # Validate attachment exists if provided
            if attachment_path and not Path(attachment_path).exists():
                return {
                    "status": "failed",
                    "message": f"Attachment not found: {attachment_path}",
                    "email": to_email
                }

            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject

            if cc_emails:
                msg['Cc'] = ", ".join(cc_emails)

            msg.attach(MIMEText(body, 'plain'))

            if attachment_path:
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(
                        f.read(),
                        Name=Path(attachment_path).name
                    )
                part['Content-Disposition'] = f'attachment; filename="{Path(attachment_path).name}"'
                msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return {
                "status": "success",
                "message": "Email sent successfully",
                "email": to_email
            }

        except smtplib.SMTPException as e:
            return {
                "status": "failed",
                "message": f"SMTP error: {str(e)}",
                "email": to_email
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Unexpected error: {str(e)}",
                "email": to_email
            }

# Pre-configured instance for easy import
email_sender = EmailSender()