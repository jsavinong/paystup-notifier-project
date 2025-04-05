"""Data Models for Payroll Processing

Defines the structure and validation rules for payroll data using Pydantic models.
Ensures data integrity before processing paystubs and sending notifications.
"""

from pydantic import BaseModel, EmailStr
from typing import List

class EmployeePayroll(BaseModel):
    """Represents an employee's payroll data for paystub generation.
    
    Validates all input data and ensures proper formatting before processing.

    Attributes:
        full_name (str): Employee's full name
        email (EmailStr): Validated email address
        position (str): Job position/title
        health_discount_amount (float): Health insurance deduction
        social_discount_amount (float): Social security deduction  
        taxes_discount_amount (float): Income tax deduction
        other_discount_amount (float): Other deductions
        gross_salary (float): Total salary before deductions
        gross_payment (float): Payment amount before taxes
        net_payment (float): Final payment amount after all deductions
        period (str): Pay period in 'YYYY-MM-DD' format

    Example:
        {
            "full_name": "John Doe",
            "email": "john@company.com",
            "position": "Developer",
            "health_discount_amount": 50.0,
            "social_discount_amount": 100.0,
            "taxes_discount_amount": 75.0,
            "other_discount_amount": 25.0,
            "gross_salary": 3000.0,
            "gross_payment": 2800.0,
            "net_payment": 2600.0,
            "period": "2023-12-15"
        }
    """
    full_name: str
    email: EmailStr  # Validates email format automatically
    position: str
    health_discount_amount: float
    social_discount_amount: float
    taxes_discount_amount: float
    other_discount_amount: float
    gross_salary: float
    gross_payment: float
    net_payment: float
    period: str  # Format: "yyyy-mm-dd"