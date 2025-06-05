from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import bcrypt

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = 'users'

	user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	username = db.Column(db.String(80), unique=True, nullable=False, index=True)
	password = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	full_name = db.Column(db.String(200), nullable=False)
	role = db.Column(db.String(20), nullable=False, default='user')
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	accounts = db.relationship('Account', backref='user', lazy=True, cascade='all, delete-orphan')
	loans = db.relationship('Loan', backref='user', lazy=True, cascade='all, delete-orphan')

	def __init__(self, username, password, email, full_name, role='user'):
		self.username = username
		self.email = email
		self.full_name = full_name
		self.role = role
		self.password = self._hash_password(password) if not password.startswith('$2b$') else password

	def _hash_password(self, password):
		password_bytes = password.encode('utf-8')
		salt = bcrypt.gensalt()
		hashed = bcrypt.hashpw(password_bytes, salt)
		return hashed.decode('utf-8')

	def verify_password(self, password):
		password_bytes = password.encode('utf-8')
		hashed_bytes = self.password.encode('utf-8')
		return bcrypt.checkpw(password_bytes, hashed_bytes)

	def to_dict(self):
		return {
			'user_id': self.user_id,
			'username': self.username,
			'email': self.email,
			'full_name': self.full_name,
			'role': self.role,
			'created_at': self.created_at.isoformat()
		}


class Account(db.Model):
	__tablename__ = 'accounts'

	account_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
	account_type = db.Column(db.String(20), nullable=False)  # Checking, Savings
	balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.0)
	account_number = db.Column(db.String(20), unique=True, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	active = db.Column(db.Boolean, nullable=False, default=True)

	# FIX -- specified which foreign_keys to use
	transactions = db.relationship('Transaction',
	                               foreign_keys='Transaction.account_id',
	                               backref='account',
	                               lazy=True,
	                               cascade='all, delete-orphan')

	destination_transactions = db.relationship('Transaction',
	                                           foreign_keys='Transaction.destination_account_id',
	                                           backref='destination_account',
	                                           lazy=True)

	def __init__(self, user_id, account_type, balance=0.0, account_number=None):
		self.user_id = user_id
		self.account_type = account_type
		self.balance = float(balance)
		self.account_number = account_number or self._generate_account_number()

	def _generate_account_number(self):
		return f"10{str(uuid.uuid4().int)[:7]}"

	def to_dict(self):
		return {
			'account_id': self.account_id,
			'user_id': self.user_id,
			'account_type': self.account_type,
			'balance': float(self.balance),
			'account_number': self.account_number,
			'created_at': self.created_at.isoformat(),
			'active': self.active
		}


class Transaction(db.Model):
	__tablename__ = 'transactions'

	transaction_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	account_id = db.Column(db.String(36), db.ForeignKey('accounts.account_id'), nullable=False)
	transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, transfer
	amount = db.Column(db.Numeric(15, 2), nullable=False)
	description = db.Column(db.Text)
	destination_account_id = db.Column(db.String(36), db.ForeignKey('accounts.account_id'), nullable=True)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def to_dict(self):
		return {
			'transaction_id': self.transaction_id,
			'account_id': self.account_id,
			'transaction_type': self.transaction_type,
			'amount': float(self.amount),
			'description': self.description,
			'destination_account_id': self.destination_account_id,
			'created_at': self.created_at.isoformat()
		}


class Loan(db.Model):
	__tablename__ = 'loans'

	loan_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
	loan_type = db.Column(db.String(20), nullable=False)  # Personal, Home, Auto, Education, Business
	amount = db.Column(db.Numeric(15, 2), nullable=False)
	interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
	term_months = db.Column(db.Integer, nullable=False)
	purpose = db.Column(db.Text)
	status = db.Column(db.String(20), nullable=False,
	                   default='pending')  # pending, approved, rejected, active, paid_off, defaulted
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	approved_at = db.Column(db.DateTime, nullable=True)
	balance = db.Column(db.Numeric(15, 2), nullable=False)

	def __init__(self, user_id, loan_type, amount, interest_rate, term_months, purpose=None, status='pending',
	             balance=None):
		self.user_id = user_id
		self.loan_type = loan_type
		self.amount = float(amount)
		self.interest_rate = float(interest_rate)
		self.term_months = int(term_months)
		self.purpose = purpose
		self.status = status
		self.balance = float(balance) if balance is not None else float(amount)

	def calculate_monthly_payment(self):
		monthly_rate = float(self.interest_rate) / 100 / 12
		if monthly_rate == 0:
			return float(self.amount) / self.term_months

		monthly_payment = (float(self.amount) * monthly_rate) / (1 - (1 + monthly_rate) ** -self.term_months)
		return round(monthly_payment, 2)

	def make_payment(self, amount):
		if amount <= 0:
			raise ValueError("Payment amount must be positive")

		if self.status != 'active':
			raise ValueError(f"Cannot make payment on loan with status '{self.status}'")

		self.balance = float(self.balance) - amount

		if self.balance <= 0:
			self.status = 'paid_off'
			self.balance = 0

		return float(self.balance)

	def approve_loan(self):
		if self.status != 'pending':
			raise ValueError(f"Cannot approve loan with status '{self.status}'")

		self.status = 'approved'
		self.approved_at = datetime.utcnow()
		return True

	def activate_loan(self):
		if self.status != 'approved':
			raise ValueError(f"Cannot activate loan with status '{self.status}'")

		self.status = 'active'
		return True

	def reject_loan(self):
		if self.status != 'pending':
			raise ValueError(f"Cannot reject loan with status '{self.status}'")

		self.status = 'rejected'
		return True

	def to_dict(self):
		return {
			'loan_id': self.loan_id,
			'user_id': self.user_id,
			'loan_type': self.loan_type,
			'amount': float(self.amount),
			'interest_rate': float(self.interest_rate),
			'term_months': self.term_months,
			'purpose': self.purpose,
			'status': self.status,
			'created_at': self.created_at.isoformat(),
			'approved_at': self.approved_at.isoformat() if self.approved_at else None,
			'balance': float(self.balance)
		}