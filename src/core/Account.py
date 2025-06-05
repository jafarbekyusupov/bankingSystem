import uuid
from datetime import datetime

class Account:
    ACCOUNT_TYPES = ['Checking', 'Savings'] # two types of accs - checking & saving

    def __init__(self, user_id, account_type, balance=0.0, account_number=None,
                 account_id=None, created_at=None, active=True):
        if account_type not in self.ACCOUNT_TYPES: raise ValueError(f"Account type must be one of {self.ACCOUNT_TYPES}")
        self.account_id = account_id if account_id else str(uuid.uuid4())
        self.user_id = user_id
        self.account_type = account_type
        self.balance = float(balance)
        self.account_number = account_number if account_number else self._generate_account_number()
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.active = active

    def _generate_account_number(self): return f"10{str(uuid.uuid4().int)[:7]}"

    def deposit(self, amount):
        if amount <= 0: raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount <= 0: raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance: raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance

    def to_dict(self): # dict -- account data as dict
        return{ 'account_id': self.account_id,'user_id': self.user_id,'account_type': self.account_type,'balance': self.balance,'account_number': self.account_number,'created_at': self.created_at,'active': self.active}

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data['user_id'],
            account_type=data['account_type'],
            balance=data['balance'],
            account_number=data['account_number'],
            account_id=data.get('account_id'),
            created_at=data.get('created_at'),
            active=data.get('active', True)
        )