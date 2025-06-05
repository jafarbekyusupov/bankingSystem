from src.models import db, Loan
# from datetime import datetime

class LoanManager:

	def get_all_loans(self): return Loan.query.all()
	def get_loan_by_id(self,loan_id): return Loan.query.filter_by(loan_id=loan_id).first()
	def get_user_loans(self, user_id): return Loan.query.filter_by(user_id=user_id).all()

	def create_loan_application(self,loan_data):
		try:
			# create new loan
			loan = Loan(user_id=loan_data['user_id'],loan_type=loan_data['loan_type'],amount=loan_data['amount'],interest_rate=loan_data['interest_rate'],term_months=loan_data['term_months'],purpose=loan_data.get('purpose'))
			db.session.add(loan)
			db.session.commit()
			return loan.loan_id
		except Exception as e:
			db.session.rollback()
			return None

	def update_loan(self, loan_id, loan_data):
		try:
			loan = self.get_loan_by_id(loan_id)
			if not loan: return False

			# more fields can be updated while pending | after approval -- only purpose field can be updated
			allowFlds = ['loan_type', 'amount', 'interest_rate', 'term_months', 'purpose'] if loan.status == 'pending' else ['purpose']

			for key, value in loan_data.items():
				if hasattr(loan, key) and key in allowFlds: setattr(loan,key,value) # upd loan fields

			db.session.commit()
			return True
		except Exception as e:
			db.session.rollback()
			return False

	def approve_loan(self, loan_id):
		try:
			loan = self.get_loan_by_id(loan_id)
			if not loan: raise ValueError("loan not found")
			loan.approve_loan()
			db.session.commit()
			return True
		except ValueError: raise
		except Exception as e:
			db.session.rollback()
			raise e

	def reject_loan(self, loan_id):
		try:
			loan = self.get_loan_by_id(loan_id)
			if not loan: raise ValueError("loan not found")
			loan.reject_loan()
			db.session.commit()
			return True
		except ValueError: raise
		except Exception as e:
			db.session.rollback()
			raise e

	def activate_loan(self, loan_id):
		try:
			loan = self.get_loan_by_id(loan_id)
			if not loan: raise ValueError("loan not found")
			loan.activate_loan()
			db.session.commit()
			return True
		except ValueError: raise
		except Exception as e:
			db.session.rollback()
			raise e

	def make_payment(self, loan_id, amount):
		try:
			loan = self.get_loan_by_id(loan_id)
			if not loan: raise ValueError("loan not found")
			new_balance = loan.make_payment(amount)
			db.session.commit()
			return new_balance
		except ValueError: raise
		except Exception as e:
			db.session.rollback()
			raise e

	def calculate_payment(self, loan_id):
		loan = self.get_loan_by_id(loan_id)
		if not loan: raise ValueError("loan not found")
		return loan.calculate_monthly_payment()