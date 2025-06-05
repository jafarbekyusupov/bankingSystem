from src.models import db, Account, Transaction, User

class AccountManager: # mng acc ops w DB

	# ===== getters ===== #
	def get_all_accounts(self): return Account.query.all()
	def get_account_by_id(self, account_id): return Account.query.filter_by(account_id=account_id).first()
	def get_user_accounts(self, user_id): return Account.query.filter_by(user_id=user_id).all()
	# =================== #

	def create_account(self, account_data):
		try:
			acc = Account(user_id=account_data['user_id'],account_type=account_data['account_type'],balance=account_data.get('balance', 0.0),account_number=account_data.get('account_number'))
			db.session.add(acc)
			db.session.commit()
			if acc.balance>0: self._create_transaction(acc.account_id,'deposit',acc.balance,'initial deposit')
			return acc.account_id
		except Exception as e: db.session.rollback(); raise e

	def update_account(self, account_id, account_data): # bool
		try:
			acc = self.get_account_by_id(account_id)
			if not acc: return False

			for key, value in account_data.items():
				if hasattr(acc, key) and key not in ['account_id', 'balance']: setattr(acc, key, value)

			db.session.commit()
			return True
		except Exception as e: db.session.rollback(); return False

	def close_account(self, account_id): #bool | check for non zero values
		try:
			acc = self.get_account_by_id(account_id)
			if not acc: return False
			if acc.balance != 0: raise ValueError("cannot close account with non-zero balance")
			acc.active = False
			db.session.commit()
			return True
		except ValueError: raise
		except Exception as e: db.session.rollback(); return False

	def deposit(self, account_id, amount, description=None): # new balance
		try:
			acc = self.get_account_by_id(account_id)
			if not acc: raise ValueError("account not found")
			if not acc.active: raise ValueError("cannot deposit to inactive account")
			if amount <= 0: raise ValueError("Deposit amount must be positive")

			acc.balance = float(acc.balance) + amount
			db.session.commit()
			self._create_transaction(account_id,'deposit',amount, description or 'deposit') # transac hstry
			return float(acc.balance)
		except ValueError: raise
		except Exception as e: db.session.rollback(); raise e

	def withdraw(self, account_id, amount, description=None): # new balance if succs else none
		try:
			acc = self.get_account_by_id(account_id)
			if not acc: raise ValueError("account not found")
			if not acc.active: raise ValueError("cannot withdraw from inactive account")
			if amount <= 0: raise ValueError("Withdrawal amount must be positive")
			if amount>acc.balance: raise ValueError("Insufficient funds")

			acc.balance = float(acc.balance) - amount
			db.session.commit()

			# create transaction record
			self._create_transaction(account_id,'withdrawal',amount,description or 'withdrawal')
			return float(acc.balance)
		except ValueError: raise
		except Exception as e: db.session.rollback(); raise e

	def transfer(self, from_account_id, to_account_id, amount, description=None): #bpol
		try:
			from_account = self.get_account_by_id(from_account_id)
			to_account = self.get_account_by_id(to_account_id)

			if not from_account or not to_account: raise ValueError("one or both accounts not found")
			if not from_account.active or not to_account.active: raise ValueError("cannot transfer to/from inactive account")
			if amount <= 0: raise ValueError("transfer amount must be POSITIVE")
			if amount>from_account.balance: raise ValueError("Insufficient funds")

			# transfer -- minus from "from" acc | plus to "to" acc
			from_account.balance = float(from_account.balance)-amount
			to_account.balance = float(to_account.balance)+amount

			db.session.commit()

			# create transaction record
			self._create_transaction(from_account_id,'transfer',amount,description or 'transfer',to_account_id)
			return True
		except ValueError: raise
		except Exception as e: db.session.rollback(); raise e

	def get_transactions(self, account_id=None, user_id=None): #list of transac objs
		#filer transacs of user
		if account_id:
			return Transaction.query.filter((Transaction.account_id == account_id) | (Transaction.destination_account_id == account_id)).order_by(Transaction.created_at.desc()).all()
		elif user_id: # get user's accs
			accs = self.get_user_accounts(user_id)
			accIds = [acc.account_id for acc in accs]
			return Transaction.query.filter((Transaction.account_id.in_(accIds)) | (Transaction.destination_account_id.in_(accIds))).order_by(Transaction.created_at.desc()).all()

		return Transaction.query.order_by(Transaction.created_at.desc()).all()

	def get_transaction_by_id(self, transaction_id): return Transaction.query.filter_by(transaction_id=transaction_id).first()

	def _create_transaction(self, account_id, transaction_type, amount, description, destination_account_id=None):
		try:
			transaction = Transaction(account_id=account_id,transaction_type=transaction_type,amount=amount,description=description,destination_account_id=destination_account_id)
			db.session.add(transaction)
			db.session.commit()
			return transaction.transaction_id
		except Exception as e: db.session.rollback(); return None