"""Paystub Processing API

FastAPI application that handles:
- Authentication for payroll processing
- CSV file upload and validation
- Paystub PDF generation
- Email distribution of paystubs

Main Endpoint:
- POST /process: Accepts CSV file and processes payroll data

Security:
- HTTP Basic Authentication
- File size and type validation
- Rate limiting for email sending
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse
from app.models import EmployeePayroll
from app.config import settings
from app.pdf_generator import generate_paystub
from app.email_sender import email_sender
from app.emailtemplates import get_paystub_email_template
import pandas as pd
import tempfile
import shutil
from typing import List, Dict
from pydantic import ValidationError
import os
import uuid
from pathlib import Path
import time

app = FastAPI()
security = HTTPBasic()

# Directory for storing generated paystubs
PAYSTUB_OUTPUT_DIR = "generated_paystubs"
Path(PAYSTUB_OUTPUT_DIR).mkdir(exist_ok=True)

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify HTTP Basic Authentication credentials.
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        str: Username if authentication succeeds
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    correct_username = settings.AUTH_USERNAME
    correct_password = settings.AUTH_PASSWORD
    
    if (credentials.username != correct_username or 
        credentials.password != correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
def home():
    """Home endpoint for API health check."""
    return "Holaaaaaaaaaa AtDev Team!"

@app.post("/process")
async def process_payroll(
    file: UploadFile,
    country: str = "do",
    company: str = "atdev",
    username: str = Depends(authenticate),
    send_emails: bool = True
):
    """Process payroll CSV and distribute paystubs.
    
    Args:
        file: CSV file containing payroll data
        country: Country code for localization (do/en)
        company: Company name for logo selection
        username: Authenticated username (from basic auth)
        send_emails: Whether to send emails (default: True)
        
    Returns:
        dict: Processing results including:
            - status: success/partial_success/error
            - employee_count: Number of valid records
            - generated_paystubs: Number of PDFs created
            - emails_sent: Number of emails successfully sent
            - errors: List of processing errors (if any)
            
    Raises:
        HTTPException: 400 for invalid CSV, 413 for large files
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {max_size/1024/1024}MB"
        )

    try:
        # Save uploaded CSV temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Read CSV into DataFrame
        try:
            df = pd.read_csv(tmp_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CSV format: {str(e)}"
            )

        # Process and validate each row
        employees = []
        errors = []
        generated_paystubs = []
        email_results = []

        for idx, row in df.iterrows():
            try:
                # Convert pandas row to dict and handle NaN values
                row_data = row.where(pd.notnull(row), None).to_dict()
                employee = EmployeePayroll(**row_data)
                employees.append(employee)
                
                # Generate PDF paystub
                try:
                    pdf_filename = generate_paystub(
                        employee=employee,
                        company=company,
                        country=country,
                        logo_dir=settings.LOGO_DIR
                    )
                    
                    # Move to our output directory
                    unique_id = uuid.uuid4().hex[:6]
                    final_path = os.path.join(PAYSTUB_OUTPUT_DIR, f"{unique_id}_{pdf_filename}")
                    os.rename(pdf_filename, final_path)
                    
                    generated_paystubs.append({
                        "employee": employee.full_name,
                        "file": final_path,
                        "email": employee.email
                    })
                    
                    # Send email with paystub
                    if send_emails:
                        subject, body = get_paystub_email_template(
                            employee.full_name,
                            country
                        )
                        
                        # Small delay to prevent rate limiting
                        time.sleep(1)  
                        
                        email_result = email_sender.send_email(
                            to_email=employee.email,
                            subject=subject,
                            body=body,
                            attachment_path=final_path,
                            cc_emails=["hr@company.com"]
                        )
                        
                        email_results.append({
                            "employee": employee.full_name,
                            "email": employee.email,
                            "status": email_result["status"],
                            "message": email_result["message"]
                        })

                except Exception as pdf_error:
                    errors.append({
                        "row": idx + 1,
                        "error": f"PDF generation failed: {str(pdf_error)}",
                        "type": "pdf_generation"
                    })
                    
            except ValidationError as e:
                errors.append({
                    "row": idx + 1,
                    "data": row_data,
                    "error": str(e),
                    "type": "validation"
                })

        # Prepare response
        response_data = {
            "status": "success" if not errors else "partial_success",
            "employee_count": len(employees),
            "generated_paystubs": len(generated_paystubs),
            "emails_sent": sum(1 for r in email_results if r["status"] == "success"),
            "errors": errors if errors else None,
            "message": "All records processed successfully" if not errors 
                      else f"Processed with {len(errors)} errors"
        }

        # Only include sensitive data in debug mode
        if settings.DEBUG:
            response_data.update({
                "generated_files": generated_paystubs,
                "email_results": email_results
            })

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )