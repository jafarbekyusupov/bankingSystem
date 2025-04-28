""" loan api endpoints """

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from src.managers.LoanManager import LoanManager
from src.utils.jwt_auth import admin_required, get_current_user

loan_bp = Blueprint('loans', __name__)
loan_manager = LoanManager()


@loan_bp.route('', methods=['GET'])
@jwt_required()
def get_loans():
    """ get loans for current user or all loans for admin """
    current_user = get_current_user()

    if current_user['role'] == 'admin' and request.args.get('all') == 'true':
        # admin can get all loans
        loans = loan_manager.get_all_loans()
    else:
        # regular users only get their loans
        loans = loan_manager.get_user_loans(current_user['user_id'])

    result = []
    for loan in loans:
        result.append(loan.to_dict())

    return jsonify(loans=result), 200


@loan_bp.route('/<loan_id>', methods=['GET'])
@jwt_required()
def get_loan(loan_id):
    current_user = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)

    if not loan:
        return jsonify(error="loan not found"), 404

    # check if user has access to this loan
    if current_user['role'] != 'admin' and loan.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to loan"), 403

    return jsonify(loan.to_dict()), 200


@loan_bp.route('', methods=['POST'])
@jwt_required()
def create_loan():
    """ create a new loan application """
    current_user = get_current_user()
    data = request.get_json()

    # validate required fields
    required_fields = ['loan_type', 'amount', 'interest_rate', 'term_months']

    for field in required_fields:
        if field not in data:
            return jsonify(error=f"missing required field: {field}"), 400

    # set user_id to cur user unless specified by admin
    if 'user_id' not in data or current_user['role'] != 'admin':
        data['user_id'] = current_user['user_id']

    try:
        loan_id = loan_manager.create_loan_application(data)

        if loan_id:
            return jsonify(message="loan application submitted successfully", loan_id=loan_id), 201
        else:
            return jsonify(error="failed to submit loan application"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>', methods=['PUT'])
@jwt_required()
def update_loan(loan_id):
    current_user = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)

    if not loan:
        return jsonify(error="loan not found"), 404

    # check if user has access to this loan
    if current_user['role'] != 'admin' and loan.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to loan"), 403

    # only admin can update loans that arent pending
    if loan.status != 'pending' and current_user['role'] != 'admin':
        return jsonify(error="cannot update loan after review has started"), 403

    data = request.get_json()

    result = loan_manager.update_loan(loan_id, data)

    if result:
        return jsonify(message="loan updated successfully"), 200
    else:
        return jsonify(error="failed to update loan"), 500


@loan_bp.route('/<loan_id>/approve', methods=['POST'])
@jwt_required()
@admin_required
def approve_loan(loan_id): # ADMIN ONLY
    try:
        result = loan_manager.approve_loan(loan_id)

        if result:
            return jsonify(message="loan approved successfully"), 200
        else:
            return jsonify(error="failed to approve loan"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>/reject', methods=['POST'])
@jwt_required()
@admin_required
def reject_loan(loan_id): # ADMIN ONLY
    try:
        result = loan_manager.reject_loan(loan_id)

        if result:
            return jsonify(message="loan rejected successfully"), 200
        else:
            return jsonify(error="failed to reject loan"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_loan(loan_id): # ADMIN ONLY
    try:
        result = loan_manager.activate_loan(loan_id)

        if result:
            return jsonify(message="loan activated successfully"), 200
        else:
            return jsonify(error="failed to activate loan"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>/payment', methods=['POST'])
@jwt_required()
def make_payment(loan_id):
    current_user = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)

    if not loan:
        return jsonify(error="loan not found"), 404

    # check if user has access to this loan
    if current_user['role'] != 'admin' and loan.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to loan"), 403

    data = request.get_json()

    # validate required fields
    if 'amount' not in data:
        return jsonify(error="amount is required"), 400

    try:
        amount = float(data['amount'])

        new_balance = loan_manager.make_payment(loan_id, amount)

        if new_balance is not None:
            return jsonify(message="payment successful", balance=new_balance), 200
        else:
            return jsonify(error="failed to process payment"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@loan_bp.route('/<loan_id>/payment-amount', methods=['GET'])
@jwt_required()
def calculate_payment(loan_id):
    current_user = get_current_user()
    loan = loan_manager.get_loan_by_id(loan_id)

    if not loan:
        return jsonify(error="loan not found"), 404

    # check if user has access to this loan
    if current_user['role'] != 'admin' and loan.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to loan"), 403

    try:
        payment_amount = loan_manager.calculate_payment(loan_id)

        return jsonify(
            payment_amount=payment_amount,
            term_months=loan.term_months,
            interest_rate=loan.interest_rate,
            principal=loan.amount,
            remaining_balance=loan.balance
        ), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400