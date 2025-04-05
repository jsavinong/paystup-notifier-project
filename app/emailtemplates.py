"""Email Template Manager for Paystub Notifications

Provides localized email templates for paystub distribution.
Contains predefined templates in multiple languages for consistent messaging.
"""

def get_paystub_email_template(employee_name: str, lang: str = "en") -> tuple[str, str]:
    """Get localized email subject and body for paystub notifications.
    
    Args:
        employee_name: Full name of the employee to personalize the message
        lang: Language code ('en' for English, 'do' for Dominican Spanish)
              Defaults to English if unspecified or unknown language provided

    Returns:
        tuple: (subject, body) strings in the requested language
        
    Example:
        >>> subject, body = get_paystub_email_template("John Doe", "en")
        >>> print(subject)
        'Your Paystub is Ready'
        
    Supported Languages:
        - 'en': English (default)
        - 'do': Dominican Spanish
    """
    templates = {
        "en": (
            "Your Paystub is Ready",
            f"""Dear {employee_name},\n\n"""
            """Your paystub for this period is attached.\n"""
            """Please contact HR if you have any questions.\n\n"""
            """Best regards,\nPayroll Team"""
        ),
        "do": (
            "Su Comprobante de Pago Está Listo",
            f"""Estimado/a {employee_name},\n\n"""
            """Adjunto encontrará su comprobante de pago de este período.\n"""
            """Por favor contacte a RRHH si tiene alguna pregunta.\n\n"""
            """Saludos cordiales,\nDepartamento de Nómina"""
        )
    }
    return templates.get(lang, templates["en"])