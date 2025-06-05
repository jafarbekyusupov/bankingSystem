import os
from src.app import create_app
from src.models import db

def reset_database():
	app = create_app()

	with app.app_context():
		print("dropping all existing tables...")
		db.drop_all()
		print("creating all tables w correct struct...")
		db.create_all()
		print(" +++++ DB RESET COMPLETED +++++ ")

		from src.models import User, Account, Transaction, Loan
		try:
			ucnt = User.query.count()
			accnt = Account.query.count()
			trcnt = Transaction.query.count()
			lcnt = Loan.query.count()
			print(f" -- Users table: {ucnt} records")
			print(f" -- Accounts table: {accnt} records")
			print(f" -- Transactions table: {trcnt} records")
			print(f" -- Loans table: {lcnt} records")
			print("\n +++ ALL TABLES CREATED SUCCESSFULLY +++ ")

		except Exception as e: print(f" !!! ERR VERIFYING TABLES -- {e} !!!")

if __name__ == '__main__':
	reset_database()