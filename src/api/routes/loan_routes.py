from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.managers.LoanManager import LoanManager
from src.utils.jwt_auth import admin_required, get_current_user

loan_bp = Blueprint('loans', __name__)
loan_manager = LoanManager()


@loan_bp.route('', methods=['GET'])
@jwt_required()
def get_loans():
    curUser = get_current_user()
    # admin can get all loans | regular users only get their loans
    loans = loan_manager.get_all_loans() if curUser['role']=='admin' and request.args.get('all')=='true' else loan_manager.get_user_loans(curUser['user_id'])
    res = []
    for ll in loans: res.append(ll.to_dict())
    return jsonify(loans=res),200


@loan_bp.route('/<loan_id>', methods=['GET'])
@jwt_required()
def get_loan(loan_id):
    curUser = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)
    if not loan: return jsonify(error="loan not found"), 404
    if curUser['role'] != 'admin' and loan.user_id != curUser['user_id']: return jsonify(error="unauthorized access to loan"), 403
    return jsonify(loan.to_dict()), 200


@loan_bp.route('', methods=['POST'])
@jwt_required()
def create_loan():
    curUser = get_current_user()
    data = request.get_json()
    required_fields = ['loan_type', 'amount', 'interest_rate', 'term_months']
    for ff in required_fields:
        if ff not in data: return jsonify(error=f"missing required field: {ff}"),400
    if 'user_id' not in data or curUser['role'] != 'admin': data['user_id'] = curUser['user_id']
    try:
        loan_id = loan_manager.create_loan_application(data)
        if loan_id: return jsonify(message="loan application submitted successfully", loan_id=loan_id),201
        else: return jsonify(error="failed to submit loan application"), 500
    except ValueError as e: return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>', methods=['PUT'])
@jwt_required()
def update_loan(loan_id):
    curUser = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)
    if not loan: return jsonify(error="loan not found"), 404
    if curUser['role'] != 'admin' and loan.user_id != curUser['user_id']: return jsonify(error="unauthorized access to loan"), 403
    if loan.status != 'pending' and curUser['role'] != 'admin': return jsonify(error="cannot update loan after review has started"), 403
    data = request.get_json()
    res = loan_manager.update_loan(loan_id, data)
    if res: return jsonify(message="loan updated successfully"),200
    else: return jsonify(error="failed to update loan"), 500

@loan_bp.route('/<loan_id>/payment', methods=['POST'])
@jwt_required()
def make_payment(loan_id):
    curUser = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)
    if not loan: return jsonify(error="loan not found"), 404
    if curUser['role'] != 'admin' and loan.user_id != curUser['user_id']: return jsonify(error="unauthorized access to loan"),403
    data = request.get_json()
    if 'amount' not in data: return jsonify(error="amount is required"),400
    try:
        amount = float(data['amount'])
        accId = data['account_id']

        from src.managers.AccountManager import AccountManager
        acc_manager = AccountManager()
        acc = acc_manager.get_account_by_id(accId) # get bank acc -- funds to pay the loan

        if not acc: return jsonify(error="account not found"), 404
        if curUser['role'] != 'admin' and acc.user_id != curUser['user_id']: return jsonify(error="unauthorized access to loan"), 403
        if acc.balance < amount: return jsonify(error="insufficient funds in selected account"), 400

        # withdrawing from acc first
        try: acc_manager.withdraw(accId, amount, f"Payment  for {loan.loan_type} loan")
        except ValueError as e: return jsonify(error=str(e)), 400

        # AND THEEEEEEEN MAKE LOAN PAYMENT
        newBlnc = loan_manager.make_payment(loan_id, amount)
        if newBlnc is not None:
            return jsonify(message="payment successful", balance=newBlnc), 200
        else:
            acc_manager.deposit(accId, amount, f"Refund for failed {loan.loan_type} loan payment")
            return jsonify(error="failed to process payment"), 500 # UPD -- if loan payment fails → refund to the account
    except ValueError as e: return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>/payment-amount', methods=['GET'])
@jwt_required()
def calculate_payment(loan_id):
    curUser = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)
    if not loan: return jsonify(error="loan not found"), 404
    if curUser['role'] != 'admin' and loan.user_id != curUser['user_id']: return jsonify(error="unauthorized access to loan"), 403
    try:
        payMnt = loan_manager.calculate_payment(loan_id)
        return jsonify(payment_amount=payMnt,term_months=loan.term_months,interest_rate=loan.interest_rate,principal=loan.amount,remaining_balance=loan.balance),200
    except ValueError as e: return jsonify(error=str(e)), 400

# ====================================== #
# ========== ADMIN ONLY FUNCS ========== #
# ====================================== #
@loan_bp.route('/<loan_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_loan(loan_id):
    try:
        res = loan_manager.approve_loan(loan_id)
        if res: return jsonify(message="loan approved successfully"),200
        else: return jsonify(error="failed to approve loan"),500
    except ValueError as e: return jsonify(error=str(e)),400


@loan_bp.route('/<loan_id>/reject', methods=['POST'])
@jwt_required()
@admin_required
def reject_loan(loan_id):
    try:
        res = loan_manager.reject_loan(loan_id)
        if res: return jsonify(message="loan rejected successfully"),200
        else: return jsonify(error="failed to reject loan"), 500
    except ValueError as e: return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_loan(loan_id): # ADMIN ONLY
    try:
        res = loan_manager.activate_loan(loan_id)
        if res: return jsonify(message="loan activated successfully"),200
        else: return jsonify(error="failed to activate loan"), 500
    except ValueError as e: return jsonify(error=str(e)), 400
# ====================================== #