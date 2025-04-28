""" user api endpoints """

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from src.managers.UserManager import UserManager
from src.utils.jwt_auth import generate_token, admin_required, get_current_user

user_bp = Blueprint('users', __name__)
user_manager = UserManager()


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # validate required fields
    required_fields = ['username', 'password', 'email', 'full_name']

    for field in required_fields:
        if field not in data:
            return jsonify(error=f"missing required field: {field}"), 400

    try:
        # create user
        user_id = user_manager.create_user(data)

        if user_id:
            return jsonify(message="user registered successfully", user_id=user_id), 201
        else:
            return jsonify(error="failed to register user"), 500
    except ValueError as e:
        return jsonify(error=str(e)), 400


@user_bp.route('/login', methods=['POST'])
def login():
    """
    auth & login a user
    """
    data = request.get_json()

    # validate required fields
    if 'username' not in data or 'password' not in data:
        return jsonify(error="username and password are required"), 400

    user = user_manager.authenticate_user(data['username'], data['password'])

    if user:
        # generate jwt token
        token = generate_token(user.user_id, user.username, user.role)

        return jsonify(
            message="login successful",
            token=token,
            user={
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
        ), 200
    else:
        return jsonify(error="invalid username or password"), 401


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_current_user()
    user = user_manager.get_user_by_id(current_user['user_id'])

    if not user:
        return jsonify(error="user not found"), 404

    return jsonify(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=user.created_at
    ), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_current_user()
    data = request.get_json()

    # don't allow changing username or role through this endpoint
    if 'username' in data:
        del data['username']
    if 'role' in data:
        del data['role']

    result = user_manager.update_user(current_user['user_id'], data)

    if result:
        return jsonify(message="profile updated successfully"), 200
    else:
        return jsonify(error="failed to update profile"), 500


@user_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users(): # ADMIN ONLY
    users = user_manager.get_all_users()

    result = []
    for user in users:
        result.append({
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'created_at': user.created_at
        })

    return jsonify(users=result), 200


@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id): # ADMIN ONLY
    user = user_manager.get_user_by_id(user_id)

    if not user:
        return jsonify(error="user not found"), 404

    return jsonify(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=user.created_at
    ), 200


@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id): # ADMIN ONLY
    data = request.get_json()

    result = user_manager.update_user(user_id, data)

    if result:
        return jsonify(message="user updated successfully"), 200
    else:
        return jsonify(error="failed to update user"), 500


@user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id): # ADMIN ONLY
    result = user_manager.delete_user(user_id)

    if result:
        return jsonify(message="user deleted successfully"), 200
    else:
        return jsonify(error="failed to delete user"), 500