import pytest
import os
from unittest.mock import Mock, patch
from reportlab.pdfgen.canvas import Canvas

# Import the function we want to test
# Assuming the module is named pdf_generator.py
from app.pdf_generator import generate_paystub

class TestPDFGenerator:
    """Test suite for PDF Generator functionality."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        # Create a mock employee with required attributes
        self.employee = Mock()
        self.employee.full_name = "John_Doe"
        self.employee.period = "2023-06-30"
        self.employee.position = "Software Engineer"
        self.employee.email = "john.doe@example.com"
        self.employee.gross_salary = 5000.00
        self.employee.gross_payment = 5000.00
        self.employee.health_discount_amount = 250.00
        self.employee.social_discount_amount = 150.00
        self.employee.taxes_discount_amount = 750.00
        self.employee.other_discount_amount = 50.00
        self.employee.net_payment = 3800.00
        
        # Test parameters
        self.company = "acme"
        self.country = "en"
        self.logo_dir = "test_logos"
        
        # Expected filename
        self.expected_filename = f"paystub_{self.employee.full_name}_{self.employee.period}.pdf"
        
        # Make sure the logo directory exists for testing
        if not os.path.exists(self.logo_dir):
            os.makedirs(self.logo_dir)
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Remove the generated PDF file if it exists
        if os.path.exists(self.expected_filename):
            os.remove(self.expected_filename)
            
        # Clean up test logo directory if it was created
        if os.path.exists(self.logo_dir) and not os.listdir(self.logo_dir):
            os.rmdir(self.logo_dir)
    
    @patch('app.pdf_generator.canvas.Canvas')
    def test_generate_paystub_returns_correct_filename(self, mock_canvas):
        """Test that generate_paystub returns the correct filename."""
        # Arrange
        mock_canvas_instance = Mock(spec=Canvas)
        mock_canvas.return_value = mock_canvas_instance
        
        # Act
        filename = generate_paystub(self.employee, self.company, self.country, self.logo_dir)
        
        # Assert
        assert filename == self.expected_filename
        mock_canvas_instance.save.assert_called_once()
    
    @patch('os.path.exists')
    @patch('app.pdf_generator.canvas.Canvas')
    def test_generate_paystub_uses_default_logo_if_company_logo_not_found(self, mock_canvas, mock_exists):
        """Test that generate_paystub uses default logo if company logo isn't found."""
        # Arrange
        mock_canvas_instance = Mock(spec=Canvas)
        mock_canvas.return_value = mock_canvas_instance
        
        # Mock os.path.exists to return False for company logo, True for default logo
        def side_effect(path):
            return "default.png" in path
        mock_exists.side_effect = side_effect
        
        # Act
        generate_paystub(self.employee, self.company, self.country, self.logo_dir)
        
        # Assert
        mock_canvas_instance.drawImage.assert_called_with(
            f"{self.logo_dir}/default.png", 50, 700, width=100, height=100
        )
    
    def test_generate_paystub_uses_spanish_labels_for_dominican_republic(self):
        """Test that generate_paystub uses Spanish labels for Dominican Republic country code."""
        # Act
        with patch('app.pdf_generator.canvas.Canvas') as mock_canvas:
            mock_canvas_instance = Mock(spec=Canvas)
            mock_canvas.return_value = mock_canvas_instance
            
            # Set country to Dominican Republic
            generate_paystub(self.employee, self.company, "do", self.logo_dir)
            
            # Assert Spanish title is used
            mock_canvas_instance.drawString.assert_any_call(180, 720, "COMPROBANTE DE PAGO")
    
    @patch('app.pdf_generator.canvas.Canvas')
    def test_generate_paystub_creates_pdf_file(self, mock_canvas):
        """Test that generate_paystub actually creates a PDF file."""
        # Arrange
        # Use the actual Canvas implementation instead of a mock
        mock_canvas.side_effect = lambda filename, pagesize: Canvas(filename, pagesize=pagesize)
        
        # Act
        filename = generate_paystub(self.employee, self.company, self.country, self.logo_dir)
        
        # Assert
        assert os.path.exists(filename)
        assert os.path.getsize(filename) > 0