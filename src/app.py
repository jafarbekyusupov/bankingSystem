"""
flask app setup
"""

import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager


def create_app():
    """create & config Flask app"""
    app = Flask(__name__, static_folder='../static', static_url_path='')

    # configs
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    # make sure data dir exists
    os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

    # extensoin setup
    CORS(app)
    jwt = JWTManager(app)

    # register api routes
    from src.api.routes.user_routes import user_bp
    from src.api.routes.account_routes import account_bp
    from src.api.routes.loan_routes import loan_bp

    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(account_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(loan_bp, url_prefix='/api/v1/loans')

    # create init data files if dne
    create_initial_data(app.config['DATA_FOLDER'])

    @app.route('/')
    def index():
        """Serve the main index page"""
        return send_from_directory(app.static_folder, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors"""
        return send_from_directory(app.static_folder, '404.html'), 404

    return app


def create_initial_data(data_folder):
    # create init data files if dne
    data_files = ['users.json', 'accounts.json', 'transactions.json', 'loans.json']

    for file_name in data_files:
        file_path = os.path.join(data_folder, file_name)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('[]')

    # create admin user if users.json is empty
    from src.managers.UserManager import UserManager
    user_manager = UserManager()

    if len(user_manager.get_all_users()) == 0:
        # admin user created
        user_manager.create_user({
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@example.com',
            'full_name': 'Admin User',
            'role': 'admin'
        })

        # sample user
        user_id = user_manager.create_user({
            'username': 'user',
            'password': 'user123',
            'email': 'user@example.com',
            'full_name': 'Sample User',
            'role': 'user'
        })

        # sample accounts for user
        from src.managers.AccountManager import AccountManager
        account_manager = AccountManager()

        account_manager.create_account({
            'user_id': user_id,
            'account_type': 'Checking',
            'balance': 1000.00,
            'account_number': '1000001'
        })

        account_manager.create_account({
            'user_id': user_id,
            'account_type': 'Savings',
            'balance': 5000.00,
            'account_number': '1000002'
        })