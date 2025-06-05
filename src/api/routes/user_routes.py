from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from src.managers.UserManager import UserManager
from src.utils.jwt_auth import generate_token, admin_required, get_current_user

user_bp = Blueprint('users', __name__)
user_manager = UserManager()


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    req_flds = ['username', 'password', 'email', 'full_name']
    for ff in req_flds:
        if ff not in data: return jsonify(error=f"missing required field: {ff}"), 400

    try:# create user
        user_id = user_manager.create_user(data)
        if user_id:
            return jsonify(message="user registered successfully", user_id=user_id), 201
        else:
            return jsonify(error="failed to register user"), 500
    except ValueError as e: return jsonify(error=str(e)), 400


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' not in data or 'password' not in data: return jsonify(error="username and password are required"), 400

    user = user_manager.authenticate_user(data['username'], data['password'])

    if user: # generate jwt token
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
    else: return jsonify(error="invalid username or password"), 401


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    cUser = get_current_user()
    user = user_manager.get_user_by_id(cUser['user_id'])

    if not user: return jsonify(error="user not found"), 404

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
    cUser = get_current_user()
    data = request.get_json()
    if 'username' in data: del data['username']
    if 'role' in data: del data['role']

    res = user_manager.update_user(cUser['user_id'], data)
    if res:
        return jsonify(message="profile updated successfully"), 200
    else:
        return jsonify(error="failed to update profile"), 500


@user_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users(): # ADMIN ONLY
    users = user_manager.get_all_users()

    res = []
    for user in users:
        res.append({
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'created_at': user.created_at
        })

    return jsonify(users=res), 200


@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id): # ADMIN ONLY
    user = user_manager.get_user_by_id(user_id)
    if not user: return jsonify(error="user not found"), 404

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
    res = user_manager.update_user(user_id, data)
    if res: return jsonify(message="user updated successfully"),200
    else: return jsonify(error="failed to update user"), 500


@user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id): # ADMIN ONLY
    res = user_manager.delete_user(user_id)
    if res: return jsonify(message="user deleted successfully"),200
    else: return jsonify(error="failed to delete user"),500