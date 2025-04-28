from src.core.Account import Account
from src.core.Transaction import Transaction
from src.utils.json_utils import load_json, save_json


class AccountManager:
    """ manager class for handling account operations """

    def __init__(self):
        """
        initialize the accountmanager
        """
        self.accounts_file = 'accounts.json'
        self.transactions_file = 'transactions.json'

    def get_all_accounts(self):
        """
        get all accounts

        returns: list of acc objs
        """
        accounts_data = load_json(self.accounts_file)
        return [Account.from_dict(account_data) for account_data in accounts_data]

    def get_account_by_id(self, account_id):
        """
        get an account by id

        args: account_id (str): account id

        returns: Account -- account obj if found else none
        """
        accounts = self.get_all_accounts()
        for account in accounts:
            if account.account_id == account_id:
                return account
        return None

    def get_user_accounts(self, user_id):
        """
        get all accounts for a user

        args: user_id (str): user id

        returns: list of acc objs belonging to user
        """
        accounts = self.get_all_accounts()
        return [account for account in accounts if account.user_id == user_id]

    def create_account(self, account_data):
        """
        create a new account

        args:
            account_data (dict): account data dict

        returns: str -- acc id if successful else none
        """
        # create new account
        account = Account(
            user_id=account_data['user_id'],
            account_type=account_data['account_type'],
            balance=account_data.get('balance', 0.0),
            account_number=account_data.get('account_number')
        )

        # save account
        accounts_data = load_json(self.accounts_file)
        accounts_data.append(account.to_dict())

        if save_json(self.accounts_file, accounts_data):
            # if initial balance > 0, create a deposit transaction
            if account.balance > 0:
                self._create_transaction(
                    account.account_id,
                    'deposit',
                    account.balance,
                    'initial deposit'
                )
            return account.account_id
        return None

    def update_account(self, account_id, account_data):
        """
        update an existing account

        args:
            account_id (str): account id
            account_data (dict): updated acc data

        returns: true if successful else false
        """
        account = self.get_account_by_id(account_id)
        if not account:
            return False

        # update account fields (except balance, which needs special handling)
        for key, value in account_data.items():
            if hasattr(account, key) and key not in ['account_id', 'balance']:
                setattr(account, key, value)

        accounts_data = load_json(self.accounts_file)

        for i, a in enumerate(accounts_data):
            if a['account_id'] == account_id:
                accounts_data[i] = account.to_dict()
                break

        return save_json(self.accounts_file, accounts_data)

    def close_account(self, account_id):
        """
        close an account -- mark as inactive

        args: account_id (str): account id

        returns: true if successful else false

        raises: ValueError -- if acc has NON-zero balance
        """
        account = self.get_account_by_id(account_id)
        if not account:
            return False

        if account.balance != 0:
            raise ValueError("cannot close account with non-zero balance")

        account.active = False

        # save updated acc
        accounts_data = load_json(self.accounts_file)

        # find & replace acc in list
        for i, a in enumerate(accounts_data):
            if a['account_id'] == account_id:
                accounts_data[i] = account.to_dict()
                break

        return save_json(self.accounts_file, accounts_data)

    def deposit(self, account_id, amount, description=None):
        """
        deposit money into an account

        args:
            account_id (str): account id
            amount (float): amount to deposit
            description (str, optional): transaction description

        returns: float -- new balance if successful else none

        raises: ValueError -- if acc not found OR amount is invalid
        """
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError("account not found")

        if not account.active:
            raise ValueError("cannot deposit to inactive account")

        try:
            new_balance = account.deposit(amount)

            accounts_data = load_json(self.accounts_file)

            for i, a in enumerate(accounts_data):
                if a['account_id'] == account_id:
                    accounts_data[i] = account.to_dict()
                    break

            if save_json(self.accounts_file, accounts_data):
                # create transaction record
                self._create_transaction(
                    account_id,
                    'deposit',
                    amount,
                    description or 'deposit'
                )
                return new_balance
        except ValueError as e:
            raise e

        return None

    def withdraw(self, account_id, amount, description=None):
        """
        withdraw money from an account

        args:
            account_id (str): account id
            amount (float): amount to withdraw
            description (str, optional): transac description

        returns: float -- new balance if successful else none

        raises: ValueError -- if account not found, amount is invalid, or insufficient funds
        """
        account = self.get_account_by_id(account_id)
        if not account:
            raise ValueError("account not found")

        if not account.active:
            raise ValueError("cannot withdraw from inactive account")

        try:
            new_balance = account.withdraw(amount)

            # save upd-d acc
            accounts_data = load_json(self.accounts_file)

            # find and replace acc in list
            for i, a in enumerate(accounts_data):
                if a['account_id'] == account_id:
                    accounts_data[i] = account.to_dict()
                    break

            if save_json(self.accounts_file, accounts_data):
                # create transac record
                self._create_transaction(
                    account_id,
                    'withdrawal',
                    amount,
                    description or 'withdrawal'
                )
                return new_balance
        except ValueError as e:
            raise e

        return None

    def transfer(self, from_account_id, to_account_id, amount, description=None):
        """
        transfer money between accs

        args:
            from_account_id (str): src acc id
            to_account_id (str): destination account id
            amount (float): amount to transfer
            description (str, optional): transac description

        returns: bool -- true if successful else false

        raises: ValueError -- if accounts not found, amount is invalid, or not enough moneu
        """
        from_account = self.get_account_by_id(from_account_id)
        to_account = self.get_account_by_id(to_account_id)

        if not from_account or not to_account:
            raise ValueError("one or both accounts not found")

        if not from_account.active or not to_account.active:
            raise ValueError("cannot transfer to/from inactive account")

        try:
            # withdraw from src acc
            from_account.withdraw(amount)

            # deposit to destination acc
            to_account.deposit(amount)

            # save upd accs
            accounts_data = load_json(self.accounts_file)

            # find & replace accs in list
            for i, a in enumerate(accounts_data):
                if a['account_id'] == from_account_id:
                    accounts_data[i] = from_account.to_dict()
                elif a['account_id'] == to_account_id:
                    accounts_data[i] = to_account.to_dict()

            if save_json(self.accounts_file, accounts_data):
                # create transaction record
                self._create_transaction(
                    from_account_id,
                    'transfer',
                    amount,
                    description or 'transfer',
                    to_account_id
                )
                return True
        except ValueError as e:
            raise e

        return False

    def get_transactions(self, account_id=None, user_id=None):
        """
        get transactions for an account or user

        args:
            account_id (str, optional) -- account id, default is none
            user_id (str, optional) -- user id, default is none

        returns: list -- list of transac objs
        """
        transactions_data = load_json(self.transactions_file)
        transactions = [Transaction.from_dict(t_data) for t_data in transactions_data]

        if account_id:
            # filter transactions for a specific account
            return [t for t in transactions if t.account_id == account_id or t.destination_account_id == account_id]
        elif user_id:
            # get users accs
            accounts = self.get_user_accounts(user_id)
            account_ids = [account.account_id for account in accounts]

            # filter transactions for users accs
            return [t for t in transactions if t.account_id in account_ids or t.destination_account_id in account_ids]

        return transactions

    def get_transaction_by_id(self, transaction_id):
        """
        get a transaction by id

        args: transaction_id (str) -- transaction id

        returns: transac -- transac obj if found else none
        """
        transactions_data = load_json(self.transactions_file)
        for t_data in transactions_data:
            if t_data['transaction_id'] == transaction_id:
                return Transaction.from_dict(t_data)
        return None

    def _create_transaction(self, account_id, transaction_type, amount, description, destination_account_id=None):
        """
        create a transaction record

        args:
            account_id (str): account id
            transaction_type (str): type of transaction
            amount (float): transaction amount
            description (str): transaction descrpt
            destination_account_id (str, opt): destination account id for transfers

        returns: str -- transaction id if successful else none
        """
        transaction = Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            destination_account_id=destination_account_id
        )

        transactions_data = load_json(self.transactions_file)
        transactions_data.append(transaction.to_dict())

        if save_json(self.transactions_file, transactions_data):
            return transaction.transaction_id
        return None