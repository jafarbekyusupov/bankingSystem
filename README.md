# Banking System
## A full-stack banking application with a Python Flask backend and HTML/CSS/JavaScript frontend.

## Project Structure
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
│   │   │   ├── transactions.js
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
