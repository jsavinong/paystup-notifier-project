# Paystub Notification System

## Setup Instructions
1. Clone repo: `git clone [repo-url]`
2. Run: `docker-compose up`
3. Access API at `http://localhost:8000`

## Credentials
- Email: ("Provided separately via email")
- Password:  ("Provided separately via email")

## API Documentation
```plaintext
POST /process
Params: 
  - file: CSV file
  - country: "do"|"en"
  - company: "atdev" - Company name for logo