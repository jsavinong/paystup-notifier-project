"""Unit tests for main.py paystub processing API"""

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from unittest.mock import patch, MagicMock, mock_open
import os
from io import BytesIO
from app.main import app, authenticate
import shutil

client = TestClient(app)

# Test data
VALID_CSV = b"""full_name,email,position,health_discount_amount,social_discount_amount,taxes_discount_amount,other_discount_amount,gross_salary,gross_payment,net_payment,period
John Doe,john@example.com,Developer,50.0,100.0,75.0,25.0,3000.0,2800.0,2600.0,2023-12-15"""

@pytest.fixture
def mock_settings():
    with patch('app.main.settings') as mock:
        mock.AUTH_USERNAME = "testuser"
        mock.AUTH_PASSWORD = "testpass"
        mock.DEBUG = False
        mock.LOGO_DIR = "/fake/logos"
        mock.SMTP_SERVER = "smtp.example.com"
        mock.SMTP_PORT = 587
        mock.SMTP_USERNAME = "user"
        mock.SMTP_PASSWORD = "pass"
        mock.FROM_EMAIL = "noreply@example.com"
        yield mock

@pytest.fixture
def mock_email_sender():
    with patch('app.main.email_sender') as mock:
        mock_instance = MagicMock()
        mock_instance.send_email.return_value = {
            "status": "success",
            "message": "Email sent successfully"
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_pdf_generator():
    with patch('app.main.generate_paystub') as mock:
        # Create a dummy PDF file
        pdf_path = "test_paystub.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(b"Dummy PDF content")
        mock.return_value = pdf_path
        yield mock
        # Clean up
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up generated files after each test"""
    yield
    if os.path.exists("generated_paystubs"):
        shutil.rmtree("generated_paystubs")
    os.makedirs("generated_paystubs", exist_ok=True)

def test_process_payroll_success(mock_pdf_generator, mock_email_sender, mock_settings):
    """Test successful payroll processing"""
    csv_file = BytesIO(VALID_CSV)
    
    response = client.post(
        "/process",
        files={"file": ("test.csv", csv_file)},
        data={"country": "do", "company": "testco"},
        auth=("testuser", "testpass")
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["employee_count"] == 1
    assert response_data["generated_paystubs"] == 1
    assert response_data["emails_sent"] == 1
    assert response_data["errors"] is None

def test_debug_mode(mock_pdf_generator, mock_email_sender, mock_settings):
    """Test additional debug information in response"""
    mock_settings.DEBUG = True
    
    csv_file = BytesIO(VALID_CSV)
    response = client.post(
        "/process",
        files={"file": ("test.csv", csv_file)},
        auth=("testuser", "testpass")
    )
    
    data = response.json()
    assert "generated_files" in data
    assert "email_results" in data
    assert len(data["generated_files"]) == 1
    assert len(data["email_results"]) == 1
    assert data["generated_files"][0]["file"].endswith(".pdf")
    assert data["email_results"][0]["status"] == "success"