""" UPD -- no shell access in free tier of render → impl auto db init"""

import os
import logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from src.models import db, User, Account, Loan, Transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
	app = Flask(__name__, static_folder='../static', static_url_path='')

	# prod configs
	app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
	app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

	dbUrl = os.environ.get('DATABASE_URL')
	if dbUrl:
		if dbUrl.startswith('postgres://'): dbUrl = dbUrl.replace('postgres://', 'postgresql://', 1)
		app.config['SQLALCHEMY_DATABASE_URI'] = dbUrl
		logger.info(" === using pqsl db === ")
	else: # for local dev
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking.db'
		logger.info(" === using SQLITE DB -- local === ")

	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True,'pool_recycle': 300,}

	CORS(app, origins="*")
	jwt = JWTManager(app)
	db.init_app(app)
	migrate = Migrate(app, db)

	# UPD -- AUTO INIT DB on first run
	with app.app_context():
		try: auto_initialize_database()
		except Exception as e: logger.error(f" !!! DB INIT ERRROR --  {e} !!! ")

	# api routes
	from src.api.routes.user_routes import user_bp
	from src.api.routes.account_routes import account_bp
	from src.api.routes.loan_routes import loan_bp

	app.register_blueprint(user_bp, url_prefix='/api/v1/users')
	app.register_blueprint(account_bp, url_prefix='/api/v1/accounts')
	app.register_blueprint(loan_bp, url_prefix='/api/v1/loans')

	@app.route('/')
	def index(): return send_from_directory(app.static_folder, 'index.html')

	@app.route('/<path:filename>')
	def static_files(filename):
		try: return send_from_directory(app.static_folder, filename)
		except: return send_from_directory(app.static_folder, 'index.html') # if not found → defalut route

	@app.errorhandler(404)
	def not_found(e): return send_from_directory(app.static_folder, 'index.html'), 200

	@app.route('/health')
	def health(): # UPD -- added stability check endpoint for render
		try:
			user_count = User.query.count()
			return {'status': 'healthy','service': 'banking-system','database': 'connected','users': user_count}, 200
		except Exception as e:
			return {
				'status': 'unhealthy',
				'service': 'banking-system',
				'error': str(e)},500

	# manual init endpoint | backup method
	@app.route('/init-database')
	def manual_init():
		try:
			res = auto_initialize_database()
			return jsonify(res), 200
		except Exception as e:
			return jsonify({'error': str(e)}), 500

	return app


def auto_initialize_database():
	try:
		logger.info("checking db init...")
		db.create_all()
		logger.info("DB tables verified/created")

		if User.query.count() == 0: # check if init needed
			logger.info("DB IS EMPTY → creating initial data...")

			admin_user = User(
				username='admin',
				password='admin123',
				email='admin@bankingsystem.com',
				full_name='System Administrator',
				role='admin'
			)
			db.session.add(admin_user)

			sample_user = User(
				username='user',
				password='user123',
				email='sampleuser@bankingsystem.com',
				full_name='Sample User',
				role='user'
			)
			db.session.add(sample_user)
			db.session.commit()

			logger.info(" === default users created === ")

			checking_account = Account(user_id=sample_user.user_id,account_type='Checking',balance=999999.99)
			db.session.add(checking_account)

			savings_account = Account(user_id=sample_user.user_id,account_type='Savings',balance=10000.00)
			db.session.add(savings_account)
			db.session.commit()

			logger.info(" === sample accs created === ")

			checking_transaction = Transaction(
				account_id=checking_account.account_id,
				transaction_type='deposit',
				amount=1500.00,
				description='Initial deposit'
			)
			db.session.add(checking_transaction)

			savings_transaction = Transaction(
				account_id=savings_account.account_id,
				transaction_type='deposit',
				amount=10000.00,
				description='Initial deposit'
			)
			db.session.add(savings_transaction)
			db.session.commit()

			logger.info(" === sample transacs created === ")

			ucnt = User.query.count()
			accnt = Account.query.count()
			trcnt = Transaction.query.count()

			res = {
				'status': 'initialized',
				'message': ' +++ DB INIT WAS SUCCESSFUL +++ ',
				'data': {
					'users': ucnt,
					'accounts': accnt,
					'transactions': trcnt
				},
				'credentials': {
					'admin': 'admin / admin123',
					'demo': 'demo / demo123'
				}
			}

			logger.info(f" +++ DB INIT IS DONE -- users - {ucnt} | accs - {accnt}")
			return res

		else: # db alr got data
			ucnt = User.query.count()
			accnt = Account.query.count()
			trcnt = Transaction.query.count()
			lcnt = Loan.query.count()

			res = {
				'status': 'already_initialized',
				'message': 'Database already has data',
				'data': {
					'users': ucnt,
					'accounts': accnt,
					'transactions': trcnt,
					'loans': lcnt
				}
			}

			logger.info(f" --- DB ALR INITED - users - {ucnt} | accounts - {accnt} --- ")
			return res

	except Exception as e:
		logger.error(f" !!! ERR DURING DB INIT -- {e} !!! ")
		db.session.rollback()
		raise e