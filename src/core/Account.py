import uuid
from datetime import datetime


class Account:
    """ account class representing bank acc-s """

    ACCOUNT_TYPES = ['Checking', 'Savings'] # two types of accs - checking & saving

    def __init__(self, user_id, account_type, balance=0.0, account_number=None,
                 account_id=None, created_at=None, active=True):
        """
        args:
            user_id (str): id of user who owns the account
            account_type (str): Type of account ('Checking' or 'Savings')
            balance (float, optional): init balance, default is 0.0
            account_number (str, optional): acc number, default is None -- random gen
            account_id (str, optional): unique identifier, default is None -- generates UUID
            created_at (str, optional): acc creation timestamp, default is None -- current time
            active (bool, optional): acc status, default is true
        """
        if account_type not in self.ACCOUNT_TYPES:
            raise ValueError(f"Account type must be one of {self.ACCOUNT_TYPES}")

        self.account_id = account_id if account_id else str(uuid.uuid4())
        self.user_id = user_id
        self.account_type = account_type
        self.balance = float(balance)
        self.account_number = account_number if account_number else self._generate_account_number()
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.active = active

    def _generate_account_number(self):
        """
        gen a unique account number

        returns: str -- acc number
        """

        return f"10{str(uuid.uuid4().int)[:7]}" # in real system => this would guarantee uniqueness

    def deposit(self, amount):
        """
        deposit money into bank acc

        args: amount (float) -- amount to deposit

        returns: float -- New balance

        raise: ValueError -- If amount is  negative
        """
        if amount <= 0: raise ValueError("Deposit amount must be positive")

        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        """
        withdraw money from the account

        args: amount (float) -- amount to withdraw

        returns: float -- new balance

        raises: ValueError -- If amount is negative OR goes over balance amount
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self.balance:
            raise ValueError("Insufficient funds")

        self.balance -= amount
        return self.balance

    def to_dict(self):
        """
        convert acc to dict

        returns: dict -- account data as dict
        """
        return{
            'account_id': self.account_id,
            'user_id': self.user_id,
            'account_type': self.account_type,
            'balance': self.balance,
            'account_number': self.account_number,
            'created_at': self.created_at,
            'active': self.active
        }

    @classmethod
    def from_dict(cls, data):
        """
        create acc from dict

        args: data (dict) -- acc data dict

        returns: acc -- acc obj
        """
        return cls(
            user_id=data['user_id'],
            account_type=data['account_type'],
            balance=data['balance'],
            account_number=data['account_number'],
            account_id=data.get('account_id'),
            created_at=data.get('created_at'),
            active=data.get('active', True)
        )