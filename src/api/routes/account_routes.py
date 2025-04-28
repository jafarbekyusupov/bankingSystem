""" account api endpoints """

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from src.managers.AccountManager import AccountManager
from src.utils.jwt_auth import admin_required, get_current_user

account_bp = Blueprint('accounts', __name__)
account_manager = AccountManager()


@account_bp.route('', methods=['GET'])
@jwt_required()
def get_accounts():
    """ get accs for cur user OR all accs for admin """
    current_user = get_current_user()

    if current_user['role'] == 'admin' and request.args.get('all') == 'true':
        # admin can get access to ALL accs
        accounts = account_manager.get_all_accounts()
    else: # regular users only get their accs
        accounts = account_manager.get_user_accounts(current_user['user_id'])

    result = []
    for account in accounts:
        result.append(account.to_dict())

    return jsonify(accounts=result), 200


@account_bp.route('/<account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    current_user = get_current_user()
    account = account_manager.get_account_by_id(account_id)

    if not account:
        return jsonify(error="account not found"), 404

    # check if user has access to this account
    if current_user['role'] != 'admin' and account.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to account"), 403

    return jsonify(account.to_dict()), 200


@account_bp.route('', methods=['POST'])
@jwt_required()
def create_account():
    current_user = get_current_user()
    data = request.get_json()

    # validate required fields
    required_fields = ['account_type']

    for field in required_fields:
        if field not in data:
            return jsonify(error=f"missing required field: {field}"), 400

    # set user_id to current user unless specified by admin
    if 'user_id' not in data or current_user['role'] != 'admin':
        data['user_id'] = current_user['user_id']

    try:
        account_id = account_manager.create_account(data)

        if account_id:
            return jsonify(message="account created successfully", account_id=account_id), 201
        else:
            return jsonify(error="failed to create account"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@account_bp.route('/<account_id>', methods=['PUT'])
@jwt_required()
def update_account(account_id):
    current_user = get_current_user()
    account = account_manager.get_account_by_id(account_id)

    if not account:
        return jsonify(error="account not found"), 404

    # check if user has access to this acc
    if current_user['role'] != 'admin' and account.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to account"), 403

    data = request.get_json()

    # dont allow changing balance directly
    if 'balance' in data: del data['balance']

    result = account_manager.update_account(account_id, data)

    if result:
        return jsonify(message="account updated successfully"), 200
    else:
        return jsonify(error="failed to update account"), 500


@account_bp.route('/<account_id>/close', methods=['POST'])
@jwt_required()
def close_account(account_id):
    current_user = get_current_user()
    account = account_manager.get_account_by_id(account_id)

    if not account:
        return jsonify(error="account not found"), 404

    # check if user has access to this acc
    if current_user['role'] != 'admin' and account.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to account"), 403

    try:
        result = account_manager.close_account(account_id)

        if result:
            return jsonify(message="account closed successfully"), 200
        else:
            return jsonify(error="failed to close account"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@account_bp.route('/<account_id>/deposit', methods=['POST'])
@jwt_required()
def deposit(account_id):
    current_user = get_current_user()
    account = account_manager.get_account_by_id(account_id)

    if not account:
        return jsonify(error="account not found"), 404

    # check if user has access to this acc
    if current_user['role'] != 'admin' and account.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to account"), 403

    data = request.get_json()

    # validate required fields
    if 'amount' not in data:
        return jsonify(error="amount is required"), 400

    try:
        amount = float(data['amount'])
        description = data.get('description')

        new_balance = account_manager.deposit(account_id, amount, description)

        if new_balance is not None:
            return jsonify(message="deposit successful", balance=new_balance), 200
        else:
            return jsonify(error="failed to process deposit"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@account_bp.route('/<account_id>/withdraw', methods=['POST'])
@jwt_required()
def withdraw(account_id):
    """
    withdraw money from an account
    """
    current_user = get_current_user()
    account = account_manager.get_account_by_id(account_id)

    if not account:
        return jsonify(error="account not found"), 404

    # check if user has access to this acc
    if current_user['role'] != 'admin' and account.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to account"), 403

    data = request.get_json()

    # validate required fields
    if 'amount' not in data:
        return jsonify(error="amount is required"), 400

    try:
        amount = float(data['amount'])
        description = data.get('description')

        new_balance = account_manager.withdraw(account_id, amount, description)

        if new_balance is not None:
            return jsonify(message="withdrawal successful", balance=new_balance), 200
        else:
            return jsonify(error="failed to process withdrawal"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@account_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    """
    transfer money between accounts
    """
    current_user = get_current_user()
    data = request.get_json()

    # validate required fields
    required_fields = ['from_account_id', 'to_account_id', 'amount']

    for field in required_fields:
        if field not in data:
            return jsonify(error=f"missing required field: {field}"), 400

    from_account = account_manager.get_account_by_id(data['from_account_id'])

    if not from_account:
        return jsonify(error="source account not found"), 404

    # check if user has access to the source account
    if current_user['role'] != 'admin' and from_account.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to source account"), 403

    try:
        amount = float(data['amount'])
        description = data.get('description')

        result = account_manager.transfer(
            data['from_account_id'],
            data['to_account_id'],
            amount,
            description
        )

        if result:
            return jsonify(message="transfer successful"), 200
        else:
            return jsonify(error="failed to process transfer"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@account_bp.route('/<account_id>/transactions', methods=['GET'])
@jwt_required()
def get_account_transactions(account_id):
    """
    get transactions for an account
    """
    current_user = get_current_user()
    account = account_manager.get_account_by_id(account_id)

    if not account:
        return jsonify(error="account not found"), 404

    # check if user has access to this acc
    if current_user['role'] != 'admin' and account.user_id != current_user['user_id']:
        return jsonify(error="unauthorized access to account"), 403

    transactions = account_manager.get_transactions(account_id=account_id)

    result = []
    for transaction in transactions:
        result.append(transaction.to_dict())

    return jsonify(transactions=result), 200


@account_bp.route('/user/transactions', methods=['GET'])
@jwt_required()
def get_user_transactions():
    current_user = get_current_user()

    transactions = account_manager.get_transactions(user_id=current_user['user_id'])

    result = []
    for transaction in transactions:
        result.append(transaction.to_dict())

    return jsonify(transactions=result), 200