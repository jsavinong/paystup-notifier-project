# Official Python 3.13 slim image
FROM python:3.13-slim

# Setting the working directory inside the container
WORKDIR /app


# Install system dependencies needed for PDF generation (required for ReportLab)
RUN apt-get update && apt-get install -y \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p /app/logos /app/generated_paystubs

# Environment variables (override these in docker-compose or run command)
ENV PYTHONPATH=/app \
    LOGO_DIR=/app/logos \
    
# Expose the port the app runs on
EXPOSE 8000  

# Command to run when container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]