import uuid
from datetime import datetime


class Loan:
    """ loan class representing bank loans """

    LOAN_TYPES = ['Personal', 'Home', 'Auto', 'Education', 'Business']
    LOAN_STATUS = ['pending', 'approved', 'rejected', 'active', 'paid_off', 'defaulted']

    def __init__(self, user_id, loan_type, amount, interest_rate, term_months,
                 purpose=None, status='pending', loan_id=None, created_at=None,
                 approved_at=None, balance=None):
        """
        args:
            user_id (str): ID of user applying for LOAN
            loan_type (str): type of loan
            amount (float): loan amount
            interest_rate (float): annual interest rate -- %
            term_months (int): loan duration in months
            purpose (str, optional): loan purpose, default is None
            status (str, optional): Loan status, default is 'pending'
            loan_id (str, optional): Unique identifier, default is None -- generates UUID
            created_at (str, optional): Loan application timestamp, default is None -- current time
            approved_at (str, optional): Loan approval timestamp, default is None.
            balance (float, optional): Current outstanding balance, default is None -- same as amount
        """
        if loan_type not in self.LOAN_TYPES:
            raise ValueError(f"Loan type must be one of {self.LOAN_TYPES}")

        if status not in self.LOAN_STATUS:
            raise ValueError(f"Loan status must be one of {self.LOAN_STATUS}")

        self.loan_id = loan_id if loan_id else str(uuid.uuid4())
        self.user_id = user_id
        self.loan_type = loan_type
        self.amount = float(amount)
        self.interest_rate = float(interest_rate)
        self.term_months = int(term_months)
        self.purpose = purpose
        self.status = status
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.approved_at = approved_at
        self.balance = float(balance) if balance is not None else float(amount)

    def calculate_monthly_payment(self):
        """
        calc monthly payment for loan

        returns: float -- mnth payment amount
        """
        # conv annual interest rate to monthly
        monthly_rate = self.interest_rate / 100 / 12

        # calc using loan payment formula
        if monthly_rate == 0: return self.amount / self.term_months

        monthly_payment = (self.amount * monthly_rate) / (1 - (1 + monthly_rate) ** -self.term_months)
        return round(monthly_payment, 2)

    def make_payment(self, amount):
        """
        make payment for the loan

        args: amount (float) -- payment amount

        returns: float -- rem balance

        raises: ValueError -- If amount is negative OR loan is NOT active
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        if self.status != 'active':
            raise ValueError(f"Cannot make payment on loan with status '{self.status}'")

        # deduct payment from balance
        self.balance -= amount

        # balance is zero or negative => loan is paid off
        if self.balance <= 0:
            self.status = 'paid_off'
            self.balance = 0

        return self.balance

    def approve_loan(self):
        """
        approve loan

        returns: bool -- true if loan was approved else false

        raises: ValueError -- If loan NOT in pending status
        """
        if self.status != 'pending':
            raise ValueError(f"Cannot approve loan with status '{self.status}'")

        self.status = 'approved'
        self.approved_at = datetime.now().isoformat()
        return True

    def activate_loan(self):
        """
        activate approved loan

        returns: bool: true if loan was activated else false

        raises: ValueError -- if loan is NOT in approvde status
        """
        if self.status != 'approved':
            raise ValueError(f"Cannot activate loan with status '{self.status}'")

        self.status = 'active'
        return True

    def reject_loan(self):
        """
        reject the loan

        returns: bool -- true if loan rejected else False

        raises: ValueError -- if loan is NOT in pending status
        """
        if self.status != 'pending':
            raise ValueError(f"Cannot reject loan with status '{self.status}'")

        self.status = 'rejected'
        return True

    def to_dict(self):
        """
        conve loan to dict

        returns: dict -- loan data as dict
        """
        return {
            'loan_id': self.loan_id,
            'user_id': self.user_id,
            'loan_type': self.loan_type,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'term_months': self.term_months,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at,
            'approved_at': self.approved_at,
            'balance': self.balance
        }

    @classmethod
    def from_dict(cls, data):
        """
        create loan frm dict

        args: data (dict) -- loan data dict

        returns: loan --- loan obj
        """
        return cls(
            user_id=data['user_id'],
            loan_type=data['loan_type'],
            amount=data['amount'],
            interest_rate=data['interest_rate'],
            term_months=data['term_months'],
            purpose=data.get('purpose'),
            status=data.get('status', 'pending'),
            loan_id=data.get('loan_id'),
            created_at=data.get('created_at'),
            approved_at=data.get('approved_at'),
            balance=data.get('balance')
        )