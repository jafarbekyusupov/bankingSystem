# Banking System

#### A full-stack banking application with a Python Flask backend and HTML / CSS / JavaScript frontend.

## Features

- User authentication and account management
- Multiple account types (Checking, Savings)
- Transaction history and money transfers
- Loan application and management
- Secure JWT-based authentication
- RESTful API for all banking operations
- Responsive web interface

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```
git clone https://github.com/jafarbekyusupov/bankingSystem.git
cd bankingSystem
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python run.py
```

4. Access the web application:
Open your browser and navigate to `http://localhost:5000`

## Usage

### Default Admin Account
 - Username: admin
 - Password: admin123

### Sample User Account
- Username: user
- Password: user123
> NOTE: You can also create your own User Account via Registration Form

## API Documentation
 
 The API endpoints are available at `/api/v1` and include:
 
 - User endpoints: `/api/v1/users`
 - Account endpoints: `/api/v1/accounts`
 - Transaction endpoints: `/api/v1/transactions`
 - Loan endpoints: `/api/v1/loans`
 
For detailed API documentation, see the API section in the application.

## Security Features

- Password hashing with bcrypt
- JWT authentication for API requests
- CSRF protection for web forms
- Input validation and sanitization

## Project Structure

The project follows a modular architecture with clear separation of concerns:

- `core/`: Core domain models
- `managers/`: Business logic and data management
- `api/`: RESTful API implementation
- `utils/`: Utility functions and helpers
- `static/`: Web frontend (HTML, CSS, JavaScript)
- `data/`: JSON data storage

## File Structure
```
BankingSystem/
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies
├── run.py                            # Application entry point
├── src/                              # Source code directory
│   ├── __init__.py                   # Package initialization
│   ├── app.py                        # Flask application setup
│   ├── core/                         # Core banking functionality
│   │   ├── __init__.py
│   │   ├── User.py                   # User class definition
│   │   ├── Account.py                # Account class definition
│   │   ├── Transaction.py            # Transaction class definition
│   │   ├── Loan.py                   # Loan class definition
│   ├── managers/                     # Manager classes
│   │   ├── __init__.py
│   │   ├── UserManager.py            # User management
│   │   ├── AccountManager.py         # Account management
│   │   ├── LoanManager.py            # Loan management
│   ├── utils/                        # Utility files
│   │   ├── __init__.py
│   │   ├── json_utils.py             # JSON serialization/deserialization
│   │   ├── jwt_auth.py               # JWT authentication
│   ├── api/                          # API server files
│   │   ├── __init__.py
│   │   ├── routes/                   # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── user_routes.py
│   │   │   ├── account_routes.py
│   │   │   ├── loan_routes.py
├── static/                           # Web frontend
│   ├── index.html                    # Main HTML file  
│   ├── css/                          # Stylesheets
│   │   ├── style.css
│   ├── js/                           # JavaScript files
│   │   ├── app.js
│   │   ├── api.js
│   │   ├── components/               # Frontend components
│   │   │   ├── dashboard.js
│   │   │   ├── accounts.js
│   │   │   ├── profile.js
│   │   │   ├── admin.js
│   │   │   ├── transactions.js
│   │   │   ├── transfers.js
│   │   │   ├── loans.js
├── data/                             # Data storage directory
│   ├── users.json                    # User data
│   ├── accounts.json                 # Account data
│   ├── transactions.json             # Transaction records
│   ├── loans.json                    # Loan data
├── tests/                            # Test files
│   ├── __init__.py
│   ├── test_user.py
│   ├── test_account.py
│   ├── test_loan.py
```
