import smtplib
import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Import the class we want to test
# Assuming the module is named email_sender.py
from app.email_sender import EmailSender

class TestEmailSender:
    """Test suite for Email Sender functionality."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        # Create an instance of EmailSender for testing
        self.email_sender = EmailSender()
        
        # Set up test data
        self.to_email = "recipient@example.com"
        self.subject = "Test Subject"
        self.body = "Test email body"
        self.attachment_path = "test_attachment.pdf"
        self.cc_emails = ["cc1@example.com", "cc2@example.com"]
        
    @patch('app.email_sender.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending without attachment."""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Act
        result = self.email_sender.send_email(
            self.to_email,
            self.subject,
            self.body
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["message"] == "Email sent successfully"
        assert result["email"] == self.to_email
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            self.email_sender.smtp_username, 
            self.email_sender.smtp_password
        )
        mock_server.send_message.assert_called_once()
    
    @patch('app.email_sender.Path.exists')
    @patch('app.email_sender.smtplib.SMTP')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test file content')
    def test_send_email_with_attachment(self, mock_file, mock_smtp, mock_exists):
        """Test sending email with file attachment."""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_exists.return_value = True
        
        # Act
        result = self.email_sender.send_email(
            self.to_email,
            self.subject,
            self.body,
            self.attachment_path
        )
        
        # Assert
        assert result["status"] == "success"
        mock_file.assert_called_once_with(self.attachment_path, "rb")
        mock_server.send_message.assert_called_once()
    
    @patch('app.email_sender.Path.exists')
    def test_send_email_with_missing_attachment(self, mock_exists):
        """Test sending email with non-existent attachment."""
        # Arrange
        mock_exists.return_value = False
        
        # Act
        result = self.email_sender.send_email(
            self.to_email,
            self.subject,
            self.body,
            self.attachment_path
        )
        
        # Assert
        assert result["status"] == "failed"
        assert "Attachment not found" in result["message"]
    
    @patch('app.email_sender.Path.exists')
    @patch('app.email_sender.smtplib.SMTP')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test file content')
    def test_send_email_with_cc(self, mock_file, mock_smtp, mock_exists):
        """Test sending email with CC recipients."""
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_exists.return_value = True
        
        # Act
        result = self.email_sender.send_email(
            self.to_email,
            self.subject,
            self.body,
            self.attachment_path,
            self.cc_emails
        )
        
        # Assert
        assert result["status"] == "success"
        # Verify that message was sent (would contain CC addresses)
        mock_server.send_message.assert_called_once()
    
    @patch('app.email_sender.smtplib.SMTP')
    def test_send_email_smtp_exception(self, mock_smtp):
        """Test handling of SMTP exceptions."""
        # Arrange
        mock_smtp.return_value.__enter__.side_effect = \
            smtplib.SMTPException("Authentication failed")
        
        # Act
        result = self.email_sender.send_email(
            self.to_email,
            self.subject,
            self.body
        )
        
        # Assert
        assert result["status"] == "failed"
        assert "SMTP error" in result["message"]
    
    @patch('app.email_sender.smtplib.SMTP')
    def test_environment_variables(self, mock_smtp):
        """Test that environment variables are properly used."""
        # Arrange
        test_server = "test.smtp.server"
        test_port = 587
        test_username = "test_user"
        test_password = "test_pass"
        test_from = "test@example.com"
        
        with patch.dict(os.environ, {
            "SMTP_SERVER": test_server,
            "SMTP_PORT": str(test_port),
            "SMTP_USERNAME": test_username,
            "SMTP_PASSWORD": test_password,
            "FROM_EMAIL": test_from
        }):
            # Act
            sender = EmailSender()
            
            # Assert
            assert sender.smtp_server == test_server
            assert sender.smtp_port == test_port
            assert sender.smtp_username == test_username
            assert sender.smtp_password == test_password
            assert sender.from_email == test_from
    
    @patch('app.email_sender.smtplib.SMTP')
    def test_default_values(self, mock_smtp):
        """Test that default values are properly set when environment variables are missing."""
        # Arrange
        # Rather than setting empty strings, completely remove the environment variables
        env_vars = {}
        
        # Only define existing environment variables that you want to keep
        # Leave out SMTP_SERVER, SMTP_PORT, and FROM_EMAIL to test defaults
        with patch.dict(os.environ, env_vars, clear=True):
            # Act
            sender = EmailSender()
            
            # Assert
            assert sender.smtp_server == "sandbox.smtp.mailtrap.io"
            assert sender.smtp_port == 2525
            assert sender.from_email == "payroll@company.com"