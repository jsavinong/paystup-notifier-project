"""PDF Paystub Generator

Creates professional paystub documents in PDF format with support for:
- Company branding via logos
- Localization (English/Spanish)
- Standard paystub sections (earnings, deductions, summary)
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
from datetime import datetime

def generate_paystub(employee, company, country, logo_dir):
    """Generates a localized paystub PDF for an employee.
    
    Args:
        employee: EmployeePayroll object containing all payroll data
        company: Company name for logo selection
        country: Country code ('do' for Spanish, others for English)
        logo_dir: Directory path containing company logos
        
    Returns:
        str: Filename of the generated PDF
        
    Raises:
        IOError: If PDF file cannot be created
        ValueError: If employee data is invalid
        
    Example:
        >>> filename = generate_paystub(employee, 'acme', 'do', 'logos')
        >>> print(filename)
        'paystub_John_Doe_2023-06-30.pdf'
    """
    # 1. Setup PDF and localization
    filename = f"paystub_{employee.full_name}_{employee.period}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Localization dictionary
    labels = {
        "en": {
            "title": "PAYSTUB",
            "employee": "Employee Information",
            "earnings": "Earnings",
            "deductions": "Deductions",
            "summary": "Payment Summary",
            "period": "Pay Period"
        },
        "do": {
            "title": "COMPROBANTE DE PAGO",
            "employee": "Información del Empleado",
            "earnings": "Ingresos",
            "deductions": "Deducciones",
            "summary": "Resumen de Pago",
            "period": "Período de Pago"
        }
    }
    lang = labels["do"] if country == "do" else labels["en"]

    # 2. Add logo (with error handling)
    try:
        logo_path = f"{logo_dir}/{company}.png"
        if not os.path.exists(logo_path):
            logo_path = f"{logo_dir}/default.png"
        c.drawImage(logo_path, 50, 700, width=100, height=100)
    except:
        pass  # Skip logo if any error occurs

    # 3. Header Section
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 720, lang["title"])
    c.setFont("Helvetica", 10)
    c.drawString(180, 700, f"{lang['period']}: {employee.period}")

    # 4. Employee Information Table
    employee_data = [
        ["Name/Nombre", employee.full_name],
        ["Position/Posición", employee.position],
        ["Email", employee.email]
    ]
    employee_table = Table(employee_data, colWidths=[150, 200])
    employee_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    employee_table.wrapOn(c, 400, 600)
    employee_table.drawOn(c, 50, 620)

    # 5. Earnings & Deductions Tables
    earnings_data = [
        [lang["earnings"], "Amount"],
        ["Gross Salary", f"${employee.gross_salary:.2f}"],
        ["Gross Payment", f"${employee.gross_payment:.2f}"]
    ]
    
    deductions_data = [
        [lang["deductions"], "Amount"],
        ["Health", f"-${employee.health_discount_amount:.2f}"],
        ["Social Security", f"-${employee.social_discount_amount:.2f}"],
        ["Taxes", f"-${employee.taxes_discount_amount:.2f}"],
        ["Other", f"-${employee.other_discount_amount:.2f}"]
    ]

    for i, data in enumerate([earnings_data, deductions_data]):
        t = Table(data)
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        t.wrapOn(c, 250, 400)
        t.drawOn(c, 50 if i == 0 else 310, 450)

    # 6. Net Payment Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 400, lang["summary"])
    c.setFont("Helvetica", 10)
    c.drawString(50, 380, f"Net Payment: ${employee.net_payment:.2f}")

    # 7. Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 30, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    c.save()
    return filename